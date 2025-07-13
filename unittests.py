import unittest
from engine import LogicEngine  # Предположим, что ты вынес движок в logic_engine.py

class TestLogicEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = LogicEngine()

    def test_basic_inference(self):
        self.engine.parse_line("carl is human.")
        self.engine.parse_line("all human are mortal.")
        self.engine.infer()
        self.assertIn(("carl", "is", "mortal"), self.engine.facts, "carl должен быть mortal по универсальному правилу")

    def test_variable_and_multiple_subjects(self):
        self.engine.parse_line("carl is human.")
        self.engine.parse_line("maria is human.")
        self.engine.parse_line("all human are mammal.")
        self.engine.infer()
        self.assertIn(("carl", "is", "mammal"), self.engine.facts, "carl должен быть mammal")
        self.assertIn(("maria", "is", "mammal"), self.engine.facts, "maria должна быть mammal")

    def test_condition_with_not(self):
        self.engine.parse_line("alice is human.")
        self.engine.parse_line("if ?x is human and not ?x has flu then ?x is healthy.")
        self.engine.infer()
        self.assertIn(("alice", "is", "healthy"), self.engine.facts, "alice должна быть healthy по правилу без flu")

    def test_positive_and_negative_conditions(self):
        self.engine.parse_line("john is human.")
        self.engine.parse_line("john has flu.")
        self.engine.parse_line("if ?x is human and ?x has flu then ?x is sick.")
        self.engine.infer()
        self.assertIn(("john", "is", "sick"), self.engine.facts, "john должен быть sick по правилу")

    def test_suggestion(self):
        self.engine.parse_line("tom is human.")
        self.engine.parse_line("tom has flu.")
        self.engine.parse_line('if ?x is human and ?x has flu then suggest "go to doctor".')
        self.engine.infer()
        output = []
        def mock_print(x): output.append(x)
        if "print_fn" in self.engine._handle_query.__code__.co_varnames:
            self.engine._handle_query("what should tom do", print_fn=mock_print)
        else:
            # Переопределяем print глобально временно, если print_fn не поддерживается
            import builtins
            original_print = builtins.print
            builtins.print = mock_print
            try:
                self.engine._handle_query("what should tom do")
            finally:
                builtins.print = original_print
        self.assertIn("go to doctor", output, "Рекомендация 'go to doctor' должна быть для tom")

    def test_query_is(self):
        self.engine.parse_line("anna is doctor.")
        self.engine.infer()
        output = []
        def mock_print(x): output.append(x)
        import builtins
        original_print = builtins.print
        builtins.print = mock_print
        try:
            self.engine._handle_query("is anna doctor")
        finally:
            builtins.print = original_print
        self.assertIn("yes", output, "Должно быть подтверждение, что anna doctor")

    def test_query_what_has(self):
        self.engine.parse_line("dog has tail.")
        output = []
        def mock_print(x): output.append(x)
        import builtins
        original_print = builtins.print
        builtins.print = mock_print
        try:
            self.engine._handle_query("what does dog have")
        finally:
            builtins.print = original_print
        self.assertIn("tail", output[0], "Собака должна иметь хвост")

    def test_query_who_has(self):
        self.engine.parse_line("jack has flu.")
        output = []
        def mock_print(x): output.append(x)
        import builtins
        original_print = builtins.print
        builtins.print = mock_print
        try:
            self.engine._handle_query("who has flu")
        finally:
            builtins.print = original_print
        self.assertIn("jack", output[0], "jack должен быть тем, у кого flu")

    def test_negative_inference(self):
        self.engine.parse_line("car is machine.")
        self.engine.parse_line("car has engine.")
        self.engine.parse_line("if ?x is machine and not ?x has engine then ?x is broken.")
        self.engine.infer()
        self.assertNotIn(("car", "is", "broken"), self.engine.facts, "car не должен быть broken, потому что у него есть engine")

if __name__ == '__main__':
    unittest.main()
