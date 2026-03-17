## 1. Philosophy

* Prioritize readability over cleverness
* Code is for humans first
* Prefer simple, explicit solutions

## 2. Naming

* Use clear, intention-revealing names
* No vague names (`x`, `tmp`, `data`)
* No unnecessary abbreviations
* Boolean names must read naturally:

  * `is_valid`, `has_access`

## 3. Functions

* Do one thing only
* Keep ≤ 20 lines
* Prefer ≤ 3 parameters
* Use descriptive names

## 4. Single Responsibility

* Each function/class = one responsibility
* Do not mix:

  * Business logic
  * DB logic
  * Formatting/UI

## 5. Nesting

* Max depth: 2–3 levels
* Use early returns / guard clauses

## 6. Comments

* Avoid obvious comments
* Only explain:

  * why, not what
  * complex decisions

## 7. Constants

* No magic numbers
* Use named constants

## 8. Error Handling

* Use exceptions, not error codes
* Fail fast with clear messages

## 9. DRY

* Avoid duplication
* Extract reusable logic
* Duplicate only if abstraction hurts readability

## 10. Formatting

* Consistent indentation
* Logical spacing
* High-level → low-level structure

## 11. Classes

* Small and focused
* Follow single responsibility
* Avoid large “God classes”

## 12. Testing

* Code must be testable
* Prefer pure functions
* Tests: readable, independent, fast

## 13. Avoid Over-Engineering

* Don’t build for hypothetical future
* Start simple

## 14. Code Smells (Do NOT Generate)

* Long functions (>30 lines)
* Deep nesting (>3)
* Poor naming
* Duplicate logic
* Excess comments
* Dead code
* Too many params (>4)

## 15. Output Checklist

* Clear names
* Small functions
* No deep nesting
* No magic numbers
* No duplication
* Clean error handling
* Readable without explanation

## Priority Order

1. Readability
2. Simplicity
3. Maintainability
4. Performance
