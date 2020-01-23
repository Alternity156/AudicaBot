# Public API for the Audica leaderboards

- Public API endpoint: `https://audica-api.hmxwebservices.com/`

---

## Limits

- 2000 requests per hour
- Leaderboard data is refreshed every 5 minutes

*it is recommended that you cache the response in order to avoid hitting the API limits*

---

## API Authentication

All request should include an authorization header in this format.

```shell
Authorization: X-API-KEY YOUR_API_KEY
```

*Replacing `YOUR_API_KEY` with your Audica Public API key*

---

## API Endpoints

### Leaderboard list endpoint

Get a list of the Audica leaderboards including valid platforms, and difficulties.

- `GET /public/1/leaderboards/`
- `Host: audica-api.hmxwebservices.com`

Response:

- `HTTP 200 OK`
- `content-type: application/json`

The following example uses [curl](https://curl.haxx.se/) and [jq](https://stedolan.github.io/jq/)

```shell
curl -H "Authorization: X-API-KEY YOUR_API_KEY" https://audica-api.hmxwebservices.com/public/1/leaderboards/ | jq
```

Output

```json
{
  "destiny": {
    "name": "Destiny",
    "difficulties": {
      "all": {
        "name": "All"
      },
      "beginner": {
        "name": "Beginner"
      },
      "moderate": {
        "name": "Moderate"
      },
      "advanced": {
        "name": "Advanced"
      },
      "expert": {
        "name": "Expert"
      }
    },
    "platforms": {
      "global": {
        "name": "Global"
      },
      "oculus": {
        "name": "Oculus"
      },
      "steam": {
        "name": "Steam"
      },
      "viveport": {
        "name": "VivePort"
      }
    }
  },
  "all_time_leaders": {
    "name": "All time leaders",
    "difficulties": {
      "all": {
        "name": "All"
      }
    },
    "platforms": {
      "global": {
        "name": "Global"
      }
    }
  }
}
```

In the above example:

- The songs name is `Destiny` with its shortname being `destiny`
- Valid difficulties (short names) are `all`, `beginner`, `moderate`, `advanced`, `expert`
- Valid platforms (short names) are `global`, `oculus`, `steam`, `viveport`

### Song leaderboard endpoint - Basic

Get the leaderboard for a song, difficulty, and platform.

- `GET /public/1/leaderboard/{leaderboard}/?platform={platform}&difficulty={difficulty}&page={page}&page_size={page_size}`
- `Host: audica-api.hmxwebservices.com`

Valid parameters can be obtained from the [Leaderboard list endpoint](#Leaderboard-list-endpoint)

#### URL path parameters (required)

- `leaderboard` - Song short name

#### URL query args / parameters (optional)

- `platform` - Song platform short name (defaults to `global` if none provided)
  - `global` if a valid platform will return a ranked leaderboard across all platforms.
- `difficulty` - Song difficulty short name (defaults to `all` if none provided)
  - `all` if a valid song difficulty will return a ranked leaderboard across all difficulties.
- `page` - leaderboard page number (defaults to `1` if none provided)
  - Valid page numbers are 1 to `total_pages` from initial leaderboard output
- `page_size` - Number of leaderboard object per page (defaults to `10` if none provided)
  - Valid numbers are 1 - 25

Response:

- `HTTP 200 OK`
- `content-type: application/json`

The following example uses [curl](https://curl.haxx.se/) and [jq](https://stedolan.github.io/jq/)

```shell
curl -H "Authorization: X-API-KEY YOUR_API_KEY" https://audica-api.hmxwebservices.com/public/1/leaderboard/destiny/?platform=global&difficulty=all&page=1&page_size=10 | jq
```

*The above example will get the global all difficulty, page 1, 10 objects per page leaderboard for the song Destiny.*

Output

```json
{
  "request": {
    "leaderboard": "destiny",
    "difficulty": "all",
    "platform": "global",
    "page": 1
  },
  "leaderboard": {
    "total_pages": 9,
    "page": 1,
    "total_size": 10,
    "data": [
      [
        {
          "rank": 1,
          "user": "SomeSteamUser",
          "difficulty": "expert",
          "percent": 67,
          "developer": false,
          "platform": "steam",
          "score": 67890554,
          "platform_id": "steam_1234"
        }
      ]
    ],
    ...
    "page_length": 10
  }
}
```

- `request` - The parameters from the original request
- `leaderboard`:
  - `total_pages` - Total number of pages in the leaderboard for the given page length / size
  - `page` - Current page
  - `total_size` - Total number of leaderboard objects
  - `page_length` - Current page length
  - `data` - Ordered list of json leaderboard objects
    - `rank` - Users numeric link for the given leaderboard, platform, and difficulty
    - `user` - Platform user name
    - `difficulty` - Difficulty for Song / Score
    - `percent` - Song / Score percentage
    - `developer` - True|False is the user an Harmonix developer
    - `platform` - Users platform
    - `score` - Difficulty for Song / Difficulty
    - `platform_id` - Audica ID of the user

---

### Song leaderboard endpoint - Enhanced

Get the leaderboard for a song, difficulty, and platform.

- `POST /public/1/leaderboard/`
- `Host: audica-api.hmxwebservices.com`

#### POST Data

```json
{
  "leaderboards": ["list, required"],
  "difficulty": "string, optional (default all)",
  "platform": "string, optional (default global)",
  "users": ["list, required"]
}
```

- `leaderboards` - A list of leaderboard song short names (maximum of 50 songs)
- `platform` - Song platform short name (defaults to `global` if none provided)
  - `global` if a valid platform will return a ranked leaderboard across all platforms.
- `difficulty` - Song difficulty short name (defaults to `all` if none provided)
  - `all` if a valid song difficulty will return a ranked leaderboard across all difficulties.
- `users` - A list of Audica user ID's (maximum of 10 users)

Valid parameters can be obtained from the [Leaderboard list endpoint](#Leaderboard-list-endpoint)

Response:

- `HTTP 200 OK`
- `content-type: application/json`

The following example uses [curl](https://curl.haxx.se/) and [jq](https://stedolan.github.io/jq/)

```shell
curl --request POST --data '{"leaderboards": ["collider", "destiny"], "users": ["steam_1234", "steam_5678", "oculus_1234"]}' -H "Content-Type: application/json" -H "Authorization: X-API-KEY YOUR_API_KEY" https://audica-api.hmxwebservices.com/public/1/leaderboard/ | jq
```

*The above example will get the global all difficulty, page 1, 10 objects per page leaderboard for the song Destiny.*

Output

```json
{
  "request": {
    "leaderboards": [
      "collider",
      "destiny"
    ],
    "difficulty": "all",
    "platform": "global",
    "users": [
      "steam_1234",
      "steam_5678",
      "oculus_1234"
    ]
  },
  "leaderboard": [
    {
      "leaderboard_name": "collider",
      "total_entries": 1,
      "data": [
        {
          "rank": 4,
          "score": 9906763,
          "platform_id": "steam_1234",
          "platform": "steam",
          "difficulty": "moderate",
          "full_combo": false,
          "percent": 82.6,
          "user": "some_user",
          "developer": false
        },
        ...
      ]
    },
    {
      "leaderboard_name": "destiny",
      "total_entries": 0,
      "data": [
        {
          "rank": 4,
          "score": 8349235,
          "platform_id": "oculus_1234",
          "platform": "steam",
          "difficulty": "moderate",
          "full_combo": false,
          "percent": 95.3,
          "user": "some_other_user",
          "developer": false
        },
        ...
      ]
    }
  ]
}
```

- `request` - The parameters from the original request
- `leaderboard`:
  - `data` - Ordered list of json leaderboard objects
    - `rank` - Users numeric link for the given leaderboard, platform, and difficulty
    - `user` - Platform user name
    - `difficulty` - Difficulty for Song / Score
    - `percent` - Song / Score percentage
    - `developer` - True|False is the user an Harmonix developer
    - `platform` - Users platform
    - `score` - Difficulty for Song / Difficulty
    - `platform_id` - Audica ID of the user
---
