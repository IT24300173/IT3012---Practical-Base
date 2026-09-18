class KnowledgeBase:

    def __init__(self):
        # Store unique facts
        self.facts = set()

        # Store rules as (premises, conclusion)
        self.rules = []

    def tell_fact(self, fact_string):
        """Add a fact to the knowledge base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """Add a rule to the knowledge base."""
        self.rules.append((premise_list, conclusion_string))

    def clear_facts(self):
        """Remove all current facts."""
        self.facts.clear()

    def forward_chain(self):
        """Apply rules repeatedly until no new facts are added."""

        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:

                # Only process if conclusion is not already known
                if conclusion not in self.facts:

                    # Modus Ponens:
                    # all premises must be present
                    if all(premise in self.facts for premise in premises):

                        self.facts.add(conclusion)

                        new_facts_added = True