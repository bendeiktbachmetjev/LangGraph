# LangGraph Integration Plan: Onboarding & MyCoachView Access

## Цель

Реализовать onboarding-чат с LangGraph агентом, который блокирует доступ к MyCoachView до завершения знакомства (создания индивидуального плана). После завершения onboarding — открывается доступ к MyCoachView.

---

## 1. Onboarding State Management

- **Где хранить флаг "onboarding complete":**
  - Локально: UserDefaults (SwiftUI) или в state приложения (только для session_id, не для статуса онбординга).
  - На backend: через поле `phase` в state сессии LangGraph.
- **Как определять завершение onboarding:**
  - Использовать поле `phase` в state (или ответе API):
    - Если `phase == "plan_ready"` — onboarding завершён, можно показывать MyCoachView.
    - Если `phase == "incomplete"` (или любое другое, кроме "plan_ready") — onboarding не завершён, показывать OnboardingChatView.
  - Не использовать локальные флаги для статуса онбординга — только phase из state.
- **session_id:**
  - Хранить в UserDefaults или в state приложения для восстановления сессии после перезапуска.

---

## 2. Onboarding Chat UI

- **Создать OnboardingChatView:**
  - Экран с чатом (вопрос-ответ), отображением прогресса, кнопкой отправки.
  - Интеграция с backend:
    - POST /session — создать новую сессию (если нет session_id)
    - POST /chat/{session_id} — отправлять сообщения, получать ответы и state
    - GET /topics/{session_id} — получить финальный план (12 недель)
- **UI детали:**
  - Отображать сообщения пользователя и агента
  - Прогресс (например, шаги: basic_info → goal → obstacles → plan)
  - Кнопка "Начать работу с коучем" после завершения onboarding

---

## 3. Блокировка MyCoachView

- **Проверка состояния onboarding:**
  - При попытке открыть MyCoachView — делать запрос к backend (GET /state/{session_id}) и проверять поле `phase` в state.
  - Если `phase == "plan_ready"` — показывать MyCoachView.
  - Если `phase == "incomplete"` (или любое другое, кроме "plan_ready") — показывать OnboardingChatView или заглушку с предложением пройти знакомство.
- **Варианты реализации:**
  - В ContentView или Router: if phase != "plan_ready" { show OnboardingChatView } else { show MyCoachView }

---

## 4. Переход к MyCoachView

- **После завершения onboarding:**
  - Автоматически переходить к MyCoachView
  - Сохранять session_id и state для дальнейшей работы
  - Передавать план и state в MyCoachView для отображения

---

## 5. UX детали

- **Обработка ошибок:**
  - Нет соединения, ошибка backend — показывать сообщение пользователю
- **Возможность повторного onboarding:**
  - Кнопка "Пройти знакомство заново" (если потребуется)
- **Хранение session_id:**
  - В UserDefaults для восстановления сессии
- **Безопасность:**
  - Проверять валидность session_id, очищать при logout

---

## 6. Примерная структура модулей (SwiftUI)

- `OnboardingChatView` — экран чата с коучем
- `MyCoachView` — основной экран коуча
- `OnboardingManager` (ObservableObject) — управляет состоянием onboarding, session_id, state
- `APIService` — взаимодействие с LangGraph backend (создание сессии, отправка сообщений, получение плана)
- `ContentView` — роутинг между OnboardingChatView и MyCoachView

---

## 7. Пример flow (SwiftUI pseudocode)

```swift
@StateObject var onboardingManager = OnboardingManager()

var body: some View {
    if !onboardingManager.isOnboardingComplete {
        OnboardingChatView(manager: onboardingManager)
    } else {
        MyCoachView(sessionID: onboardingManager.sessionID, plan: onboardingManager.plan)
    }
}
```

---

## 8. Следующие шаги

1. Реализовать OnboardingManager (state, API-интеграция, хранение session_id)
2. Создать OnboardingChatView (UI, логика отправки/получения сообщений)
3. Интегрировать проверку onboarding в ContentView
4. Реализовать переход к MyCoachView после завершения onboarding
5. UX polishing, обработка ошибок, тестирование

---

**Все комментарии и названия UI-элементов — только на английском!** 