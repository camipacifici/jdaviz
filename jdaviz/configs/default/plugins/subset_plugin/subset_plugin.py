from glue.core.message import EditSubsetMessage, SubsetCreateMessage
from glue.core.edit_subset_mode import (AndMode, AndNotMode, OrMode,
                                        ReplaceMode, XorMode)
from glue.core.subset import (RoiSubsetState, RangeSubsetState,
                              OrState, AndState)
from glue_jupyter.widgets.subset_mode_vuetify import SelectionModeMenu
from traitlets import List, Unicode, Bool, Dict, observe

from jdaviz.core.registries import tray_registry
from jdaviz.core.template_mixin import TemplateMixin, SubsetSelect

__all__ = ['SubsetPlugin']

SUBSET_MODES = {
    'replace': ReplaceMode,
    'add': OrMode,
    'and': AndMode,
    'xor': XorMode,
    'remove': AndNotMode
}


@tray_registry('g-subset-plugin', label="Subset Tools")
class SubsetPlugin(TemplateMixin):
    template_file = __file__, "subset_plugin.vue"
    select = List([]).tag(sync=True)
    subset_items = List([]).tag(sync=True)
    subset_selected = Unicode("No selection (create new)").tag(sync=True)
    mode_selected = Unicode('add').tag(sync=True)
    show_region_info = Bool(False).tag(sync=True)
    subset_classname = Unicode('').tag(sync=True)
    subset_definition = Dict({}).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.components = {
            'g-subset-mode': SelectionModeMenu(session=self.session)
        }

        self.session.hub.subscribe(self, EditSubsetMessage,
                                   handler=self._sync_selected_from_state)
        self.session.hub.subscribe(self, SubsetCreateMessage,
                                   handler=self._sync_available_from_state)

        self.no_selection_text = "Create new"
        self.subset_select = SubsetSelect(self,
                                          'subset_items',
                                          'subset_selected',
                                          default_text=self.no_selection_text)

    def _sync_selected_from_state(self, *args):
        if self.session.edit_subset_mode.edit_subset == []:
            if self.subset_selected != self.no_selection_text:
                self.subset_selected = self.no_selection_text
                self.show_region_info = False
        else:
            new_label = self.session.edit_subset_mode.edit_subset[0].label
            if new_label != self.subset_selected:
                self.subset_selected = self.session.edit_subset_mode.edit_subset[0].label
                self._get_region_definition(self.subset_selected)
                self.show_region_info = True

    def _sync_available_from_state(self, *args):
        self.subset_items = [{'label': self.no_selection_text}] + [
                             self.subset_select._subset_to_dict(subset) for subset in
                             self.data_collection.subset_groups]

    @observe('subset_selected')
    def _sync_selected_from_ui(self, change):
        if change['new'] != self.no_selection_text:
            self._get_region_definition(change['new'])
        self.show_region_info = change['new'] != self.no_selection_text
        m = [s for s in self.app.data_collection.subset_groups if s.label == change['new']]
        self.session.edit_subset_mode.edit_subset = m

    '''
    # This will be needed once we use a dropdown instead of the actual
    # g-subset-mode component
    @observe("mode_selected")
    def _mode_selected_changed(self, event={}):
        if self.session.edit_subset_mode != self.mode_selected:
            self.session.edit_subset_mode = self.mode_selected
    '''

    def _get_region_definition(self, subset_label):
        subset_atts = {"CircularROI": [""]}
        self.subset_definition = {}
        subset_group = [s for s in self.app.data_collection.subset_groups if
                        s.label == subset_label][0]
        subset_state = subset_group.subset_state
        subset_class = subset_state.__class__

        if subset_class in (OrState, AndState):
            self.subset_class = "Compound Subset"
        else:
            if isinstance(subset_class, RoiSubsetState):
                self.subset_classname = subset_state.roi.__class__.__name__
                if self.subset_classname == "CircularROI":
                    self.subset_definition = {"Center": subset_state.roi.get_center(),
                                              "Radius": subset_state.roi.radius}
            elif isinstance(subset_class, RangeSubsetState):
                self.subset_classname = "Range"
                self.subset_definition = {"Upper bound": subset_state.hi,
                                          "Lower bound": subset_state.lo}

