# server-the-prospector
All responses are Json

## Return values
| Statuscode | Return |
|----|----|
| 200 | `Expected return value` |
| 400 | `message: str` |
| 401 | `message: str` |
| 404 | `message: str` |

## Login
url: **/user/login/**

| Request Type | Params | Return |
|----|----|----|
| POST | `username: str`, `password: str` | `token: str` |

## Register
url: **/user/register/**

| Request Type | Params | Return |
|----|----|----|
| POST | `username: str`, `password1: str`, `password2: str`| `token: str` |

- username must be atleast 3 characters
- passwords must match and be atleast 5 characters

## Unlocked levels
Get or update the users unlocked levels

url: **/user/unlocked-level/**

| Request Type | Params | Return |
|----|----|----|
| POST | `current_level: str`| `current_level: int` |
| GET | `None`| `current_level: int` |


