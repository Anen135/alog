import re
from typing import List, Tuple, Optional, Dict

Fact = Tuple[str, str, str]  # (subject, relation, object)
Rule = Tuple[List[Fact], Fact]

class LogicEngine:
    def __init__(self):
        self.facts: List[Fact] = []
        self.rules: List[Rule] = []
        self.suggestions: List[Tuple[List[Fact], str]] = []
        self.synonyms: Dict[str, str] = {
            "is": "is",
            "equals": "is",
            "are": "is",
            "be": "is",
            "has": "has",
            "have": "has",
            "possesses": "has",
            "owns": "has",
            "can": "can",
            "able": "can",
            "requires": "requires",
            "needs": "requires",
            "must": "requires",
            "causes": "causes",
            "triggers": "causes",
            "suggest": "suggest",
            "advise": "suggest",
            "recommend": "suggest",
        }

    def _normalize_relation(self, rel: str) -> str:
        return self.synonyms.get(rel, rel)

    def parse_line(self, line: str):
        line = line.strip().lower().rstrip('.')
        if not line:
            return
        if line.startswith("if") and " then " in line:
            _, right = line.split(" then ", 1)
            first_word = right.strip().split(" ", 1)[0]
            if self._normalize_relation(first_word) == "suggest":
                self._parse_suggestion(line)
                return
            else:
                self._parse_rule(line)
                return

        if line.startswith("all"):
            self._parse_all(line)
        elif line.startswith("suggest"):
            self._parse_suggestion(line)
        elif line.startswith("what") or line.startswith("is") or line.startswith("who"):
            self._handle_query(line)
        else:
            self._parse_fact(line)

    def _parse_fact(self, line: str):
        for keyword in (" is ", " has "):
            if keyword in line:
                subj, obj = line.split(keyword, 1)
                rel = self._normalize_relation(keyword.strip())
                self.facts.append((subj.strip(), rel, obj.strip()))
                return

    def _parse_all(self, line: str):
        if " are " in line:
            _, rest = line.split("all ", 1)
            cls, prop = rest.split(" are ", 1)
            rel = self._normalize_relation("is")
            self.rules.append(([("?x", rel, cls.strip())], ("?x", rel, prop.strip())))

    def _parse_rule(self, line: str):
        conds, cons = line[3:].split(" then ", 1)
        conditions = []
        for part in conds.split(" and "):
            part = part.strip()
            neg = False
            if part.startswith("not "):
                part = part[4:]
                neg = True
            for keyword in (" is ", " has "):
                if keyword in part:
                    subj, obj = part.split(keyword, 1)
                    rel = self._normalize_relation(keyword.strip())
                    if neg:
                        rel += " not"
                    conditions.append((subj.strip(), rel, obj.strip()))
                    break
        conclusion = self._parse_fact_expr(cons.strip())
        self.rules.append((conditions, conclusion))

    def _parse_fact_expr(self, text: str) -> Fact:
        for keyword in (" is ", " has "):
            if keyword in text:
                subj, obj = text.split(keyword, 1)
                rel = self._normalize_relation(keyword.strip())
                return (subj.strip(), rel, obj.strip())
        return ("", "", "")

    def _parse_suggestion(self, line: str):
        if " then " in line and '"' in line:
            rule_part, suggestion = line.split(" then ", 1)
            action_word, rest = suggestion.strip().split(" ", 1)
            suggestion_text = rest.strip('"')
            conds = []
            conditions_text = rule_part[3:] if rule_part.startswith("if ") else rule_part
            for part in conditions_text.split(" and "):
                part = part.strip()
                neg = False
                if part.startswith("not "):
                    part = part[4:]
                    neg = True
                for keyword in (" is ", " has "):
                    if keyword in part:
                        subj, obj = part.split(keyword, 1)
                        rel = self._normalize_relation(keyword.strip())
                        if neg:
                            rel += " not"
                        conds.append((subj.strip(), rel, obj.strip()))
                        break
            self.suggestions.append((conds, suggestion_text))

    def infer(self):
        changed = True
        while changed:
            changed = False
            for conditions, conclusion in self.rules:
                for entity in self._all_subjects():
                    if self._match_conditions(entity, conditions):
                        inferred_fact = (
                            entity if conclusion[0] == "?x" else conclusion[0],
                            conclusion[1],
                            entity if conclusion[2] == "?x" else conclusion[2],
                        )
                        if inferred_fact not in self.facts:
                            self.facts.append(inferred_fact)
                            changed = True

    def _all_subjects(self) -> List[str]:
        subjects = set()
        for subj, _, obj in self.facts:
            subjects.add(subj)
            subjects.add(obj)
        for rule in self.rules:
            for cond in rule[0]:
                if not cond[0].startswith("?"):
                    subjects.add(cond[0])
                if not cond[2].startswith("?"):
                    subjects.add(cond[2])
            conc = rule[1]
            if not conc[0].startswith("?"):
                subjects.add(conc[0])
            if not conc[2].startswith("?"):
                subjects.add(conc[2])
        return list(subjects)

    def _match_conditions(self, entity: str, conditions: List[Fact]) -> bool:
        for cond in conditions:
            subj = entity if cond[0] == "?x" else cond[0]
            rel = self._normalize_relation(cond[1].replace(" not", ""))
            match = (subj, rel, cond[2]) in self.facts
            if "not" in cond[1]:
                if match:
                    return False
            else:
                if not match:
                    return False
        return True

    def _handle_query(self, line: str):
        self.infer()
        if line.startswith("is"):
            parts = line.split(" ")
            if len(parts) == 4:
                _, subj, rel, obj = parts
                rel = self._normalize_relation(rel)
                if (subj, rel, obj) in self.facts:
                    print("yes")
                else:
                    print("no")
            elif len(parts) == 3:
                _, subj, obj = parts
                if (subj, "is", obj) in self.facts:
                    print("yes")
                else:
                    print("no")
        elif line.startswith("what does"):
            m = re.match(r"what does (\w+) have", line)
            if m:
                subj = m.group(1)
                has = [obj for s, rel, obj in self.facts if s == subj and rel == "has"]
                print(", ".join(has) if has else "nothing")
        elif line.startswith("what should"):
            m = re.match(r"what should (\w+) do", line)
            if m:
                subj = m.group(1)
                for conds, suggestion in self.suggestions:
                    if self._match_conditions(subj, conds):
                        print(suggestion)
                        return
                print("no suggestion")
        elif line.startswith("who"):
            if "has" in line:
                _, _, obj = line.split(" ", 2)
                result = [s for s, rel, o in self.facts if rel == "has" and o == obj]
                print(", ".join(result) if result else "nobody")
            elif "is" in line:
                _, _, prop = line.split(" ", 2)
                result = [s for s, rel, o in self.facts if rel == "is" and o == prop]
                print(", ".join(result) if result else "nobody")
