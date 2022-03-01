import numpy as np

from bqplot.marks import Lines, Scatter

from glue.core import BaseData
from glue.core.subset import Subset
from glue.config import data_translator
from glue_jupyter.bqplot.profile import BqplotProfileView
from glue.core.exceptions import IncompatibleAttribute

from astropy import table
from specutils import Spectrum1D
from matplotlib.colors import cnames
from astropy import units as u


from jdaviz.core.registries import viewer_registry
from jdaviz.core.marks import SpectralLine
from jdaviz.core.linelists import load_preset_linelist, get_available_linelists
from jdaviz.core.freezable_state import FreezableProfileViewerState
from jdaviz.components.toolbar_nested import NestedJupyterToolbar
from jdaviz.configs.default.plugins.viewers import JdavizViewerMixin

__all__ = ['SpecvizProfileView']


@viewer_registry("specviz-profile-viewer", label="Profile 1D (Specviz)")
class SpecvizProfileView(BqplotProfileView, JdavizViewerMixin):
    # Whether to inherit tools from glue-jupyter automatically. Set this to
    # False to have full control here over which tools are shown in case new
    # ones are added in glue-jupyter in future that we don't want here.
    inherit_tools = False

    tools = ['bqplot:home',
             'jdaviz:boxzoom', 'jdaviz:xrangezoom',
             'bqplot:panzoom', 'bqplot:panzoom_x',
             'bqplot:panzoom_y', 'bqplot:xrange']

    # categories: zoom resets, zoom, pan, subset, select tools, shortcuts
    tools_nested = [
                    ['bqplot:home'],
                    ['jdaviz:boxzoom', 'jdaviz:xrangezoom'],
                    ['bqplot:panzoom', 'bqplot:panzoom_x', 'bqplot:panzoom_y'],
                    ['bqplot:xrange'],
                ]

    default_class = Spectrum1D
    spectral_lines = None
    _state_cls = FreezableProfileViewerState

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.display_uncertainties = False
        self.display_mask = False

    def initialize_toolbar_nested(self):
        self.toolbar_nested = NestedJupyterToolbar(self, self.tools_nested)

    def _on_subset_create(self, msg):
        for layer in self.state.layers:
            if layer.layer.label == msg.subset.label:
                layer.linewidth = 3

    def _on_add_data(self, msg):
        data_label = msg.data.label
        for layer in self.state.layers:
            if "Subset" in layer.layer.label and layer.layer.data.label == data_label:
                layer.linewidth = 3

    def data(self, cls=None):
        # Grab the user's chosen statistic for collapsing data
        if hasattr(self.state, 'function'):
            statistic = self.state.function
        else:
            statistic = None

        data = []

        for layer_state in self.state.layers:
            if hasattr(layer_state, 'layer'):

                # For raw data, just include the data itself
                if isinstance(layer_state.layer, BaseData):
                    _class = cls or self.default_class

                    if _class is not None:
                        # If spectrum, collapse via the defined statistic
                        if _class == Spectrum1D:
                            layer_data = layer_state.layer.get_object(cls=_class,
                                                                      statistic=statistic)
                        else:
                            layer_data = layer_state.layer.get_object(cls=_class)

                        data.append(layer_data)

                # For subsets, make sure to apply the subset mask to the
                #  layer data first
                elif isinstance(layer_state.layer, Subset):
                    layer_data = layer_state.layer

                    if _class is not None:
                        handler, _ = data_translator.get_handler_for(_class)
                        try:
                            layer_data = handler.to_object(layer_data,
                                                           statistic=statistic)
                        except IncompatibleAttribute:
                            continue
                    data.append(layer_data)

        return data

    @property
    def redshift(self):
        return self.jdaviz_helper._redshift

    def load_line_list(self, line_table, replace=False, return_table=False, show=True):
        # If string, load the named preset list and don't show by default
        # since there might be too many lines
        if isinstance(line_table, str):
            self.load_line_list(load_preset_linelist(line_table),
                                replace=replace, return_table=return_table,
                                show=False)
            return
        elif not isinstance(line_table, table.QTable):
            raise TypeError("Line list must be an astropy QTable with\
                            (minimally) 'linename' and 'rest' columns")
        if "linename" not in line_table.columns:
            raise ValueError("Line table must have a 'linename' column'")
        if "rest" not in line_table.columns:
            raise ValueError("Line table must have a 'rest' column'")

        # Use the redshift of the displayed spectrum if no redshifts are specified
        if "redshift" not in line_table.colnames:
            line_table["redshift"] = self.data()[0].spectral_axis.redshift
        # Make sure the redshift column is a quantity
        line_table["redshift"] = u.Quantity(line_table["redshift"])

        # Set whether to show all of the lines on the plot by default on load
        # We convert bool to int to work around ipywidgets json serialization
        line_table["show"] = int(show)

        # If there is already a loaded table, convert units to match. This
        # attempts to do some sane rounding after the unit conversion.
        # TODO: Fix this so that things don't get rounded to 0 in some cases
        """
        if self.spectral_lines is not None:
            sig_figs = []
            for row in line_table:
                rest_str = str(row["rest"].value).replace(".", "").split("e")[0]
                sig_figs.append(len(rest_str))
            line_table["rest"] = line_table["rest"].to(self.spectral_lines["rest"].unit)
            line_table["sig_figs"] = sig_figs
            for row in line_table:
                row["rest"] = row["rest"].round(row["sig_figs"])
            del line_table["sig_figs"]
        """

        # Combine name and rest value for indexing
        if "name_rest" not in line_table.colnames:
            line_table["name_rest"] = None
            for row in line_table:
                row["name_rest"] = "{} {}".format(row["linename"], row["rest"].value)

        # If no name was given to this list, consider it part of the "Custom" list
        if "listname" not in line_table.colnames:
            line_table["listname"] = "Custom"
        else:
            for row in line_table:
                if row["listname"] is None:
                    row["listname"] = "Custom"

        # Convert colors to hexa values, or set to default (red)
        if "colors" not in line_table.colnames:
            line_table["colors"] = "#FF0000FF"
        else:
            for row in line_table:
                if row["colors"][0] == "#":
                    if len(row["colors"]) == 6:
                        row["colors"] += "FF"
                else:
                    row["colors"] = cnames[row["colors"]] + "FF"

        # Create or update the main spectral_lines astropy table
        if self.spectral_lines is None or replace:
            self.spectral_lines = line_table
        else:
            self.spectral_lines = table.vstack([self.spectral_lines, line_table])
            self.spectral_lines = table.unique(self.spectral_lines, keys='name_rest')

        # It seems that we need to recreate this index after v-stacking.
        self.spectral_lines.add_index("name_rest")
        self.spectral_lines.add_index("linename")
        self.spectral_lines.add_index("listname")

        if return_table:
            return line_table

    def erase_spectral_lines(self, name=None, name_rest=None, show_none=True):
        """
        Erase either all spectral lines, all spectral lines sharing the same
        name (e.g. 'He II') or a specific name-rest value combination (e.g.
        'HE II 1640.5', stored in SpectralLine as 'table_index').
        """
        fig = self.figure
        if name is None and name_rest is None:
            fig.marks = [x for x in fig.marks if not isinstance(x, SpectralLine)]
            if show_none:
                self.spectral_lines["show"] = False
        else:
            temp_marks = []
            # Toggle "show" value in main astropy table. The astropy table
            # machinery only allows updating a single row at a time.
            if name_rest is not None:
                if isinstance(name_rest, str):
                    self.spectral_lines.loc[name_rest]["show"] = False
                elif isinstance(name_rest, list):
                    for nr in name_rest:
                        self.spectral_lines.loc[nr]["show"] = False
            # Get rid of the marks we no longer want
            for x in fig.marks:
                if isinstance(x, SpectralLine):
                    if name is not None:
                        self.spectral_lines.loc[name]["show"] = False
                        if x.name == name:
                            continue
                    else:
                        if isinstance(name_rest, str):
                            if x.table_index == name_rest:
                                continue
                        elif isinstance(name_rest, list):
                            if x.table_index in name_rest:
                                continue
                temp_marks.append(x)
            fig.marks = temp_marks

    def get_scales(self):
        fig = self.figure
        # Deselect any pan/zoom or subsetting tools so they don't interfere
        # with the scale retrieval
        if self.toolbar.active_tool is not None:
            self.toolbar.active_tool = None
        return {'x': fig.interaction.x_scale, 'y': fig.interaction.y_scale}

    def plot_spectral_line(self, line, plot_units=None, **kwargs):
        if isinstance(line, str):
            # Try the full index first (for backend calls), otherwise name only
            try:
                line = self.spectral_lines.loc[line]
            except KeyError:
                line = self.spectral_lines.loc["linename", line]
        if plot_units is None:
            plot_units = self.data()[0].spectral_axis.unit

        line_mark = SpectralLine(self,
                                 line['rest'].to(plot_units).value,
                                 self.redshift,
                                 name=line["linename"],
                                 table_index=line["name_rest"],
                                 colors=[line["colors"]], **kwargs)

        # Erase this line if it already existed, to avoid duplication
        self.erase_spectral_lines(name_rest=line["name_rest"])

        self.figure.marks = self.figure.marks + [line_mark]
        line["show"] = True

    def plot_spectral_lines(self, colors=["blue"], **kwargs):
        """
        Plots a user-provided astropy table of spectral lines in the viewer.
        """
        fig = self.figure
        self.erase_spectral_lines(show_none=False)

        # Check to see if colors were defined for each line
        if "colors" in self.spectral_lines.columns:
            colors = self.spectral_lines["colors"]
        elif len(colors) != len(self.spectral_lines):
            colors = colors*len(self.spectral_lines)

        lines = self.spectral_lines
        plot_units = self.data()[0].spectral_axis.unit

        marks = []
        for line, color in zip(lines, colors):
            if not line["show"]:
                continue
            line = SpectralLine(self,
                                line['rest'].to(plot_units).value,
                                redshift=self.redshift,
                                name=line["linename"],
                                table_index=line["name_rest"],
                                colors=[color], **kwargs)
            marks.append(line)
        fig.marks = fig.marks + marks

    def available_linelists(self):
        return get_available_linelists()

    def show_uncertainties(self):
        self.display_uncertainties = True
        self._plot_uncertainties()

    def show_mask(self):
        self.display_mask = True
        self._plot_mask()

    def clean(self):
        self.display_uncertainties = False
        self.display_mask = False

        marks = self.figure.marks[:]

        # Remove extra traces, in case they exist.
        self._clean_error(marks)
        self._clean_mask(marks)

        self.figure.marks = marks

    def _clean_mask(self, marks):
        if hasattr(self, 'mask_line_mark') and self.mask_line_mark is not None:
            marks.remove(self.mask_line_mark)
            self.mask_line_mark = None
            self.mask_trace_pointer = None

    def _clean_error(self, marks):
        if hasattr(self, 'error_line_mark') and self.error_line_mark is not None:
            marks.remove(self.error_line_mark)
            self.error_line_mark = None
            self.error_trace_pointer = None

    def add_data(self, data, color=None, alpha=None, **layer_state):
        """
        Overrides the base class to add markers for plotting
        uncertainties and data quality flags.

        Parameters
        ----------
        spectrum : :class:`glue.core.data.Data`
            Data object with the spectrum.
        color : obj
            Color value for plotting.
        alpha : float
            Alpha value for plotting.

        Returns
        -------
        result : bool
            `True` if successful, `False` otherwise.
        """
        # The base class handles the plotting of the main
        # trace representing the spectrum itself.
        result = super().add_data(data, color, alpha, **layer_state)

        # Index of spectrum trace plotted by the super class. It is the
        # **latest** item in figure.marks that is a Line instance
        for ind, mark in reversed(list(enumerate(self.figure.marks))):
            # we'll use __class__.__name__ since other entries (spectral lines,
            # etc) defined in jdaviz.core.marks inherit from Lines
            if mark.__class__.__name__ == 'Lines':
                self.data_trace_pointer = ind
                break
        else:  # pragma: no cover
            raise ValueError("could not find mark for added data")

        self.error_trace_pointer = None
        self.mask_trace_pointer = None

        # Color and opacity are taken from the already plotted trace,
        # in case they are not set explicitly by the caller.
        self._color = self.figure.marks[self.data_trace_pointer].colors[0]
        if color:
            self._color = color

        self._alpha = self.figure.marks[self.data_trace_pointer].opacities[0]
        if alpha:
            self._alpha = alpha

        # An opacity defined specifically for the shaded areas.
        self._alpha_shade = self._alpha / 3

        self._plot_uncertainties()

        self._plot_mask()

        return result

    def _plot_mask(self):

        _data = self._data[0]
        _data_trace = self.data_trace_pointer

        if 'mask' in _data.components and self.display_mask:

            # If a mask was already plotted, remove it.
            if (hasattr(self, 'mask_trace_pointer') and
                    self.mask_trace_pointer is not None):
                marks = self.figure.marks[:]
                self._clean_mask(marks)
                self.figure.marks = marks

            mask = _data['mask'].data

            # get trace with spectrum.
            x = self.figure.marks[_data_trace].x
            y = self.figure.marks[_data_trace].y

            # For plotting markers only for the masked data
            # points, erase un-masked data from trace.
            y = np.where(np.asarray(mask) == 0, np.nan, y)

            # there is no 'X' marker option in bqplot
            self.mask_line_mark = Scatter(scales=self.scales,
                                          marker='cross',
                                          x=x,
                                          y=y,
                                          stroke_width=0.5,
                                          # colors=['red'],
                                          colors=[self._color],
                                          default_size=25,
                                          default_opacities=[self._alpha],
                                          )
            self.figure.marks = list(self.figure.marks) + [self.mask_line_mark]

            # We added an extra trace. Get pointer to it.
            self.mask_trace_pointer = len(self.figure.marks) - 1

    def _plot_uncertainties(self):

        _data = self._data[0]
        _data_trace = self.data_trace_pointer

        if 'uncertainty' in _data.components and self.display_uncertainties:
            error = np.array(_data['uncertainty'].data)

            # If uncertainties were already plotted, remove them.
            if (hasattr(self, 'error_trace_pointer') and
                    self.error_trace_pointer is not None):
                marks = self.figure.marks[:]
                self._clean_error(marks)
                self.figure.marks = marks

            # The shaded band around the spectrum trace is bounded by
            # two lines, above and below the spectrum trace itself.
            x = np.array([np.ndarray.tolist(self.figure.marks[_data_trace].x),
                          np.ndarray.tolist(self.figure.marks[_data_trace].x)])
            y = np.array([np.ndarray.tolist(self.figure.marks[_data_trace].y - error),
                          np.ndarray.tolist(self.figure.marks[_data_trace].y + error)])

            # A Lines bqplot instance with two lines and shaded area
            # in between.
            self.error_line_mark = Lines(scales=self.scales,
                                         x=[x],
                                         y=[y],
                                         stroke_width=1,
                                         colors=[self._color, self._color],
                                         fill_colors=[self._color, self._color],
                                         opacities=[0.0, 0.0],
                                         fill_opacities=[self._alpha_shade, self._alpha_shade],
                                         fill='between',
                                         close_path=False
                                         )
            self.figure.marks = list(self.figure.marks) + [self.error_line_mark]

            # We added an extra trace. Get pointer to it.
            self.error_trace_pointer = len(self.figure.marks) - 1

    def set_plot_axes(self):
        # Get data to be used for axes labels
        data = self.data()[0]

        # Set axes labels for the spectrum viewer
        spectral_axis_unit_type = str(data.spectral_axis.unit.physical_type).title()
        # flux_unit_type = data.flux.unit.physical_type.title()
        flux_unit_type = "Flux density"

        if data.spectral_axis.unit.is_equivalent(u.m):
            spectral_axis_unit_type = "Wavelength"
        elif data.spectral_axis.unit.is_equivalent(u.pixel):
            spectral_axis_unit_type = "pixel"

        label_0 = f"{spectral_axis_unit_type} [{data.spectral_axis.unit.to_string()}]"
        self.figure.axes[0].label = label_0
        self.figure.axes[1].label = f"{flux_unit_type} [{data.flux.unit.to_string()}]"

        # Make it so y axis label is not covering tick numbers.
        self.figure.axes[1].label_offset = "-50"

        # # Set Y-axis to scientific notation
        self.figure.axes[1].tick_format = '0.1e'
