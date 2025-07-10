# Swift Integration Guide for MentorAI Backend

## 1. Firebase Auth Setup (iOS)

- Подключи Firebase SDK к своему Xcode-проекту (через Swift Package Manager или CocoaPods).
- Включи нужные методы авторизации (например, Email/Password, Google, Apple и т.д.) в консоли Firebase.
- Настрой GoogleService-Info.plist в проекте.

## 2. Получение idToken пользователя

```swift
import FirebaseAuth

func getFirebaseIdToken(completion: @escaping (String?) -> Void) {
    if let user = Auth.auth().currentUser {
        user.getIDToken { token, error in
            if let token = token {
                completion(token)
            } else {
                print("Error getting idToken: \(error?.localizedDescription ?? "unknown error")")
                completion(nil)
            }
        }
    } else {
        completion(nil)
    }
}
```

## 3. Отправка запросов к backend с токеном

```swift
import Foundation

func sendChatMessage(sessionId: String, message: String, idToken: String, completion: @escaping (String?) -> Void) {
    guard let url = URL(string: "https://<YOUR_BACKEND_URL>/chat/\(sessionId)") else { return }
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.setValue("Bearer \(idToken)", forHTTPHeaderField: "Authorization")
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    let body: [String: Any] = ["message": message]
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)

    let task = URLSession.shared.dataTask(with: request) { data, response, error in
        guard let data = data, error == nil else {
            completion(nil)
            return
        }
        if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
           let reply = json["reply"] as? String {
            completion(reply)
        } else {
            completion(nil)
        }
    }
    task.resume()
}
```

## 4. Пример использования

```swift
getFirebaseIdToken { idToken in
    guard let idToken = idToken else { return }
    sendChatMessage(sessionId: "YOUR_SESSION_ID", message: "Hello!", idToken: idToken) { reply in
        print("Bot reply: \(reply ?? "No reply")")
    }
}
```

## 5. Переменные окружения (на Railway)
- `FIREBASE_CREDENTIALS_JSON` — весь JSON из приватного ключа Firebase
- `MONGODB_URI` — строка подключения к MongoDB
- `OPENAI_API_KEY` — ключ OpenAI

## 6. Важно
- Все запросы к backend должны содержать header:
  - `Authorization: Bearer <idToken>`
- Без валидного токена backend вернёт 401 Unauthorized
- Не забывай обновлять idToken, если пользователь перелогинился

## 7. Ошибки
- 401 — неверный или просроченный токен (перелогинь пользователя)
- 404 — неверный session_id
- 500 — ошибка сервера (логируй и сообщай пользователю)

---

**Если потребуется пример для других endpoints или расширенная интеграция — дай знать!** 