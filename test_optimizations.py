"""
Тестовий файл для перевірки оптимізацій та безпеки
"""
import sys
import time
from database import (
    validate_email, validate_phone, validate_price, validate_integer,
    sanitize_string, add_account, add_dish, add_feedback
)

def test_validation():
    """Тестування функцій валідації"""
    print("\n=== Тестування валідації ===\n")
    
    # Email валідація
    test_emails = [
        ("test@example.com", True),
        ("invalid-email", False),
        ("user@domain", False),
        ("user@domain.com", True),
        ("", False)
    ]
    
    print("📧 Email валідація:")
    for email, expected in test_emails:
        result = validate_email(email)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{email}' -> {result} (очікується {expected})")
    
    # Phone валідація
    test_phones = [
        ("+380501234567", True),
        ("0501234567", True),
        ("12345", False),
        ("", False),
        ("+38 (050) 123-45-67", True)
    ]
    
    print("\n📱 Phone валідація:")
    for phone, expected in test_phones:
        result = validate_phone(phone)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{phone}' -> {result} (очікується {expected})")
    
    # Price валідація
    test_prices = [
        (100.50, True),
        (-10, False),
        (0, True),
        (999999.99, True),
        (1000000, False),
        ("abc", False)
    ]
    
    print("\n💰 Price валідація:")
    for price, expected in test_prices:
        result = validate_price(price)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{price}' -> {result} (очікується {expected})")
    
    # Sanitization
    test_strings = [
        ("<script>alert('xss')</script>", "scriptalert('xss')/script"),
        ("Normal text", "Normal text"),
        ("Test<>symbols", "Testsymbols"),
    ]
    
    print("\n🧹 String sanitization:")
    for text, expected_contains in test_strings:
        result = sanitize_string(text)
        has_dangerous = '<' in result or '>' in result
        status = "✓" if not has_dangerous else "✗"
        print(f"  {status} '{text}' -> '{result}'")


def test_database_validation():
    """Тестування валідації при додаванні в БД"""
    print("\n\n=== Тестування database валідації ===\n")
    
    # Тест некоректного email
    print("🧪 Тест: Додавання користувача з некоректним email")
    try:
        add_account("John", "Doe", "+380501234567", "invalid-email")
        print("  ✗ FAIL: Мало б викинути ValueError")
    except ValueError as e:
        print(f"  ✓ PASS: {e}")
    except Exception as e:
        print(f"  ✗ FAIL: Несподівана помилка: {e}")
    
    # Тест некоректного телефону
    print("\n🧪 Тест: Додавання користувача з некоректним телефоном")
    try:
        add_account("Jane", "Smith", "123", "jane@example.com")
        print("  ✗ FAIL: Мало б викинути ValueError")
    except ValueError as e:
        print(f"  ✓ PASS: {e}")
    except Exception as e:
        print(f"  ✗ FAIL: Несподівана помилка: {e}")
    
    # Тест некоректної ціни
    print("\n🧪 Тест: Додавання страви з некоректною ціною")
    try:
        add_dish("Test Dish", -100, "image.jpg", "desc", "ingr", 100)
        print("  ✗ FAIL: Мало б викинути ValueError")
    except ValueError as e:
        print(f"  ✓ PASS: {e}")
    except Exception as e:
        print(f"  ✗ FAIL: Несподівана помилка: {e}")
    
    # Тест XSS в feedback
    print("\n🧪 Тест: Додавання feedback з XSS спробою")
    try:
        result = add_feedback(
            "<script>alert('xss')</script>",
            "test@example.com",
            "<img src=x onerror=alert('xss')>"
        )
        print(f"  ✓ PASS: Дані sanitized та додані (id: {result})")
    except ValueError as e:
        print(f"  ✓ PASS: Відхилено: {e}")
    except Exception as e:
        print(f"  ⚠ WARNING: {e}")


def test_performance():
    """Базове тестування продуктивності"""
    print("\n\n=== Тестування продуктивності ===\n")
    
    # Тест швидкості валідації
    iterations = 10000
    
    print(f"⏱️ Тест швидкості email валідації ({iterations} ітерацій):")
    start = time.time()
    for _ in range(iterations):
        validate_email("test@example.com")
    duration = time.time() - start
    print(f"  Час: {duration:.3f}s ({iterations/duration:.0f} ops/sec)")
    
    print(f"\n⏱️ Тест швидкості sanitization ({iterations} ітерацій):")
    start = time.time()
    for _ in range(iterations):
        sanitize_string("<script>alert('test')</script>")
    duration = time.time() - start
    print(f"  Час: {duration:.3f}s ({iterations/duration:.0f} ops/sec)")


def main():
    """Запуск всіх тестів"""
    print("=" * 60)
    print("🧪 ТЕСТУВАННЯ ОПТИМІЗАЦІЙ ТА БЕЗПЕКИ")
    print("=" * 60)
    
    try:
        test_validation()
        test_database_validation()
        test_performance()
        
        print("\n" + "=" * 60)
        print("✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
        print("=" * 60)
        print("\nПримітка: Деякі тести можуть вимагати активної БД.")
        print("Для повного тестування запустіть Flask застосунок.")
        
    except Exception as e:
        print(f"\n❌ КРИТИЧНА ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
