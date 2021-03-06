# server-the-prospector
All responses are Json

**Once a login has been successfully made, the `token` must be included in the Authentication header in all methods that have authentication set to true**

Format: `Authentication: Token token` \
Where the latter 'token' is the actual token received and the first is a string. Seperated by whitespace.

## Return values
| Statuscode | Return |
|----|----|
| 200 | `Expected return value` |
| 400 | `message: str` |
| 401 | `message: str` |
| 404 | `message: str` |

## Login
url: **/user/login/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| POST | `username: str`, `password: str` | `token: str` | False |

## Guest login
url: **/user/guest-login/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| GET | `None`| `token: str` | False |

## Register
url: **/user/register/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| POST | `username: str`, `password1: str`, `password2: str`| `token: str` | False |

- username must be atleast 3 characters
- passwords must match and be atleast 5 characters

## Unlocked levels
Get or update the users unlocked levels

url: **/user/unlocked-level/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| POST | `unlocked_level: int`| `current_level: int` | True |
| GET | `None`| `unlocked_level: int` | True |


## Save Level results (Without score/stars)
Save only the users results of the completed level (restarts, time and what level) \
url: **/user/save-playstats/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| POST | `restarts: int`, `level: int`, `time: float` | `message: str`, `data: dict`| True |

Json/Dict contains all updated values given as params

## Best times
Get the best time for each level the user has played \
url: **/user/best-time/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| GET | `None` |`level: list(int)`, `time: list(float)`| True |

## Best level time
Get the users best time in a  given level \
url: **/user/best-time/<int:level>/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| GET | `None` |`time: float`| True |


## All Level stars
Get all of the users stars from all level\
url: **/user/level-stars/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| GET | `None` |`levels: list (int)`, `stars: list (int)`| True |

## Single level stars
Get or update a users stars on a single level\
url: **/user/level-stars/<int:level>/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| GET | `None` | `level: int`, `stars: int`| True |
| POST | `level: int`, `stars: int` | `message: str`, `level: int`, `stars: int` | True |

## Post game update (Update all)
Update all users data at once after a game\
url: **/user/post-game-update/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| POST | `level: int`, `stars: int`, `restarts: int`, `time: float` | `message: str`| True |

## World record
Get the best time on a given level.\
url: **world-record-time/<int:level>/**

| Request Type | Params | Return | Auth Required |
|----|----|----|----|
| GET | `level: int`| `message: str`| False |
