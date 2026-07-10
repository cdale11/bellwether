"""v0.8.4 bounded presentation-only horror.

This layer never mutates geography, evidence, memories, portraits, or canonical prose.
It derives short-lived, auditable presentation instructions only from authoritative active
horror overlays and recurrence/psychology state.
"""
from copy import deepcopy

KIND_EFFECTS = {
    'spatial_misalignment': ['map_contradiction'],
    'routine_desync': ['text_dislocation'],
    'acoustic_displacement': ['text_dislocation', 'portrait_tonal_shift'],
    'timetable_contradiction': ['journal_inconsistency'],
    'recognition_failure': ['portrait_tonal_shift', 'journal_inconsistency'],
    'ecological_contradiction': ['theme_mismatch'],
    'textual_repetition': ['text_repetition', 'journal_inconsistency'],
}

class InterfaceHorrorModel:
    def runtime_defaults(self):
        return {'schema_version': 1, 'seen_effects': [], 'presentation_log': []}

    def migrate(self, state):
        root = state.setdefault('interface_horror', self.runtime_defaults())
        for k, v in self.runtime_defaults().items(): root.setdefault(k, deepcopy(v))
        root['schema_version'] = 1
        return root

    def resolve(self, state):
        """Return display instructions; authoritative state is never changed."""
        root = self.migrate(state)
        loc = state.get('location')
        overlay = state.get('systemic_horror', {}).get('active_overlays', {}).get(loc)
        if not overlay:
            return {'active': False, 'effects': [], 'source': None, 'strength': 0}
        kind = overlay.get('kind')
        allowed = list(KIND_EFFECTS.get(kind, []))
        strength = max(1, min(3, int(overlay.get('strength', 1))))
        # Keep early corruption restrained: one effect at strength 1, two at higher strength.
        effects = allowed[:1 if strength == 1 else 2]
        source = overlay.get('anomaly_id')
        for effect in effects:
            token = f'{source}:{effect}'
            if token not in root['seen_effects']:
                root['seen_effects'].append(token)
                root['presentation_log'].append({'day': state.get('day'), 'pulse': overlay.get('pulse'), 'location': loc, 'source': source, 'effect': effect, 'strength': strength})
        root['presentation_log'] = root['presentation_log'][-50:]
        return {'active': bool(effects), 'effects': effects, 'source': source, 'kind': kind, 'strength': strength, 'location': loc}

    def developer_context(self, state):
        root = self.migrate(state)
        return {'current': self.resolve(state), 'seen_effects': deepcopy(root['seen_effects']), 'recent_log': deepcopy(root['presentation_log'][-12:]), 'authority': 'presentation_only'}

INTERFACE_HORROR_MODEL = InterfaceHorrorModel()
