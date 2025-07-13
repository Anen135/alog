from engine import LogicEngine

engine = LogicEngine()

# === Загрузка демо-файла ===
def load_file(path: str):
    with open(path, encoding="utf-8") as f:
        for line in f:
            engine.parse_line(line)

# Загрузим демо-логику и запросы
load_file("data/ELD.alog")

# Инференция
engine.infer()

# === Встроенные действия системы ===
def check_compliance(entity):
    for fact in engine.facts:
        if fact[0] == entity and fact[1] == "requires":
            req = fact[2]
            if (entity, "has", req) not in engine.facts:
                print(f"[SYSTEM] {entity} is missing required: {req}")
                return
    print(f"[SYSTEM] {entity} is compliant.")

# === Рекомендации/предпочтения пользователю ===
def advise_management(entity):
    print(f"> what should {entity} do")
    engine._handle_query(f"what should {entity} do")

# Загрузим и выполним тестовые вопросы
print("=== ECONOMIC SYSTEM CHECK ===")
check_compliance("acme_inc")

print("\n=== MANAGEMENT ADVICE ===")
load_file("data/ELD_tests.alogq")
