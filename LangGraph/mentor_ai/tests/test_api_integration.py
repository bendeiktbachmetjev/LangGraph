import pytest
import requests
import time

BASE_URL = "http://localhost:8000"

def test_full_flow():
    # 1. Create session
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    session_id = data["session_id"]
    
    # 2. Send message to chat (оба поля)
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    # Wait a bit to ensure DB is ready
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "reply" in chat_data
    assert chat_data["session_id"] == session_id
    print("Reply from LLM (оба поля):", chat_data["reply"])

def test_ask_age_if_only_name():
    # 1. Create session
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]
    
    # 2. Send message to chat (только имя)
    chat_payload = {"message": "Hi, my name is John."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    print("Reply from LLM (только имя):", chat_data["reply"])
    assert "age" in chat_data["reply"].lower() or "old" in chat_data["reply"].lower() 

def test_full_onboarding_flow():
    """Simulate full onboarding: name -> age -> goal type -> branch"""
    import requests
    import time
    BASE_URL = "http://localhost:8000"

    # 1. Create session
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 2. Send only name
    chat_payload = {"message": "Hi, my name is John."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    print("Reply after name:", chat_data["reply"])
    assert "age" in chat_data["reply"].lower() or "old" in chat_data["reply"].lower()

    # 3. Send only age
    chat_payload = {"message": "I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    print("Reply after age:", chat_data["reply"])
    # Должен быть вопрос про цель (classify_category)
    assert "goal" in chat_data["reply"].lower() or "career" in chat_data["reply"].lower() or "relationship" in chat_data["reply"].lower()

    # 4. Send goal type (career)
    chat_payload = {"message": "I want to improve my career."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    print("Reply after goal type:", chat_data["reply"])
    # Должен быть вопрос из improve_intro (или аналогичной ветки)
    assert "job" in chat_data["reply"].lower() or "position" in chat_data["reply"].lower() or "role" in chat_data["reply"].lower() 

def test_carrier_intro_flow():
    """CarrierIntroTest: Полный flow до improve_intro и проверка перехода к career_goal"""
    # 1. Create session
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 2. Send only name
    chat_payload = {"message": "Hi, my name is John."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "age" in chat_data["reply"].lower() or "old" in chat_data["reply"].lower()

    # 3. Send only age
    chat_payload = {"message": "I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    # Должен быть вопрос про цель
    assert "goal" in chat_data["reply"].lower() or "career" in chat_data["reply"].lower() or "relationship" in chat_data["reply"].lower()

    # 4. Send goal type (career)
    chat_payload = {"message": "I want to improve my career."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    # Должно быть интро-сообщение из improve_intro
    assert "career" in chat_data["reply"].lower()
    # CarrierIntroTest завершён успешно 

def test_career_category_clarification():
    """Проверка, что бот переспросит при неясном ответе на classify_category (и career_goal, если реализован)"""
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 1. Имя и возраст (быстро доходим до classify_category)
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "goal" in chat_data["reply"].lower() or "career" in chat_data["reply"].lower() or "relationship" in chat_data["reply"].lower()

    # 2. Неясный ответ на classify_category
    chat_payload = {"message": "I don't know, maybe something..."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    # Бот должен переспросить, а не перейти к intro
    assert "goal" in chat_data["reply"].lower() or "could you clarify" in chat_data["reply"].lower() or "not sure" in chat_data["reply"].lower() or "please specify" in chat_data["reply"].lower()
    # Не должен быть переход к improve_intro/find_intro/...
    assert not ("career" in chat_data["reply"].lower() and "steps" in chat_data["reply"].lower()) 

def test_career_full_flow_http():
    """Интеграционный тест: полный flow по ветке career через HTTP, включая переспросы"""
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 1. Имя и возраст (быстро доходим до classify_category)
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "goal" in chat_data["reply"].lower() or "career" in chat_data["reply"].lower() or "relationship" in chat_data["reply"].lower()

    # 2. Выбор career
    chat_payload = {"message": "I want to improve my career."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "career" in chat_data["reply"].lower() and "step" in chat_data["reply"].lower() or "goal" in chat_data["reply"].lower()

    # 3. career_goal: неясный ответ (должен быть переспрос)
    chat_payload = {"message": "I don't know, maybe something..."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "goal" in chat_data["reply"].lower() or "clarify" in chat_data["reply"].lower()

    # 4. career_goal: валидный ответ
    chat_payload = {"message": "I want to become a CTO."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "obstacle" in chat_data["reply"].lower() or "challenge" in chat_data["reply"].lower()

    # 5. improve_obstacles: неясный ответ (должен быть переспрос)
    chat_payload = {"message": "I don't know, maybe something..."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "obstacle" in chat_data["reply"].lower() or "clarify" in chat_data["reply"].lower()

    # 6. improve_obstacles: валидный ответ
    chat_payload = {"message": "Lack of experience and confidence."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "thank" in chat_data["reply"].lower() or "understand" in chat_data["reply"].lower() or "obstacle" in chat_data["reply"].lower() 

def test_career_to_plan_http():
    """Интеграционный тест: полный flow по ветке career до career_to_plan через HTTP"""
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 1. Имя и возраст
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "goal" in chat_data["reply"].lower() or "career" in chat_data["reply"].lower() or "relationship" in chat_data["reply"].lower()

    # 2. Выбор career
    chat_payload = {"message": "I want to improve my career."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "career" in chat_data["reply"].lower() and "step" in chat_data["reply"].lower() or "goal" in chat_data["reply"].lower()

    # 3. career_goal
    chat_payload = {"message": "I want to become a CTO."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    assert "obstacle" in chat_data["reply"].lower() or "challenge" in chat_data["reply"].lower()

    # 4. improve_obstacles
    chat_payload = {"message": "Lack of experience and confidence."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    # Должно быть exit-сообщение
    assert "thank" in chat_data["reply"].lower() and "plan" in chat_data["reply"].lower()
    print("Exit message:", chat_data["reply"]) 

def test_real_generate_plan_http():
    """Реальный интеграционный тест: полный карьерный flow до генерации плана, выводит 12-недельный план"""
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 1. Имя и возраст
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 2. Выбор career
    chat_payload = {"message": "I want to improve my career."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 3. career_goal
    chat_payload = {"message": "I want to become a CTO."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 4. improve_obstacles
    chat_payload = {"message": "Lack of experience and confidence."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 5. career_to_plan (автоматический переход)
    chat_payload = {"message": ""}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    if resp.status_code != 200:
        print("\n=== SERVER ERROR BODY ===")
        print(resp.text)
        print("========================\n")
    assert resp.status_code == 200

    # 6. generate_plan (автоматический переход)
    chat_payload = {"message": ""}
    time.sleep(1.0)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200
    chat_data = resp.json()
    print("\n=== REAL 12-WEEK PLAN OUTPUT ===")
    print("Reply:", chat_data.get("reply"))
    plan = chat_data.get("plan")
    if plan:
        for i in range(1, 13):
            print(f"Week {i} Topic:", plan.get(f"week_{i}_topic"))
    print("Next:", chat_data.get("next"))
    print("==============================\n") 

def test_get_goal_http():
    """Интеграционный тест: пройти карьерный flow и получить цель через GET /goal/{session_id}"""
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 1. Имя и возраст
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 2. Выбор career
    chat_payload = {"message": "I want to improve my career."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 3. career_goal
    chat_payload = {"message": "I want to become a CTO."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 4. improve_obstacles
    chat_payload = {"message": "Lack of experience and confidence."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 5. career_to_plan (автоматический переход)
    chat_payload = {"message": ""}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 6. generate_plan (автоматический переход)
    chat_payload = {"message": ""}
    time.sleep(1.0)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 7. GET /goal/{session_id}
    resp = requests.get(f"{BASE_URL}/goal/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    print("\n=== GOAL ENDPOINT OUTPUT ===")
    print("session_id:", data.get("session_id"))
    print("goal:", data.get("goal"))
    print("===========================\n") 

def test_get_topics_http():
    """Интеграционный тест: пройти карьерный flow и получить 12-недельный план через GET /topics/{session_id}"""
    resp = requests.post(f"{BASE_URL}/session")
    assert resp.status_code == 200
    data = resp.json()
    session_id = data["session_id"]

    # 1. Имя и возраст
    chat_payload = {"message": "Hi, my name is John and I'm 25."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 2. Выбор career
    chat_payload = {"message": "I want to improve my career."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 3. career_goal
    chat_payload = {"message": "I want to become a CTO."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 4. improve_obstacles
    chat_payload = {"message": "Lack of experience and confidence."}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 5. career_to_plan (автоматический переход)
    chat_payload = {"message": ""}
    time.sleep(0.5)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 6. generate_plan (автоматический переход)
    chat_payload = {"message": ""}
    time.sleep(1.0)
    resp = requests.post(f"{BASE_URL}/chat/{session_id}", json=chat_payload)
    assert resp.status_code == 200

    # 7. GET /topics/{session_id}
    resp = requests.get(f"{BASE_URL}/topics/{session_id}")
    assert resp.status_code == 200
    data = resp.json()
    print("\n=== TOPICS ENDPOINT OUTPUT ===")
    print("session_id:", data.get("session_id"))
    topics = data.get("topics")
    if topics:
        for i in range(1, 13):
            print(f"Week {i} Topic:", topics.get(f"week_{i}_topic"))
    print("==============================\n") 