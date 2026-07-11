# AI Usage

This project was developed with AI assistance. I used AI as a planning, coding, debugging, and review partner, while retaining responsibility for the scope, design decisions, validation, and final implementation.

## Tools used

- **ChatGPT** — planning, explaining unfamiliar backend concepts, suggesting implementation approaches, generating initial test code, debugging, and documentation support
- **GitHub Copilot** — inline code completion and a final readability and maintainability review
- **Warp** — terminal command suggestions and command completion

## How I used AI

### Planning and system design

I initially used ChatGPT to confirm my understanding of the task and create a time-boxed implementation plan.

AI helped me explore:

- the API request and response shape
- possible fraud rules and risk scores
- options for storing payment history
- an initial project structure
- suitable test scenarios

I challenged several early suggestions where they felt too complex for the scope. For example, the first proposed structure separated the application into five modules before any code had been written. I chose to begin with a single `main.py` and only introduced `rules.py` and `database.py` once their separate responsibilities became clear through implementation.

I also challenged the initial payment-velocity scoring proposal. Rather than applying different scores to the third and fourth payments, I chose one clear velocity rule worth 50 points. This allowed multiple independent risk signals to combine naturally into a block decision.

I added the very-high-value payment rule and selected a £25,000 threshold, recognising that Allica serves business customers for whom lower payment thresholds may be routine. The rule thresholds remain illustrative and would require calibration using real transaction and fraud data.

### Implementation

ChatGPT suggested code approaches for:

- defining and validating the payment request with FastAPI and Pydantic
- implementing individual fraud rules
- calculating the overall risk score and decision
- storing and querying payment history with SQLite
- returning structured reason codes
- handling duplicate payment IDs and invalid amounts

GitHub Copilot was primarily used for inline completion rather than generating large sections through chat. I reviewed generated code before retaining it and only kept code I could explain.

Warp suggested and completed terminal commands. I reviewed commands before running them, particularly where they affected processes, dependencies, Git, or local files.

### Testing

I identified the key behaviours that needed testing, then used ChatGPT to help translate those scenarios into pytest code.

The tests cover:

- individual fraud rules
- approve, review, and block outcomes
- combinations of risk signals
- payment velocity across multiple API requests
- isolated temporary databases for API tests
- duplicate payment IDs
- invalid negative payment amounts

I reviewed the inputs and expected results, ran the tests locally, and manually exercised the API using FastAPI’s `/docs` interface and a curl request.

The final implementation has 16 passing tests.

### Code review and documentation

I used ChatGPT to create a tightly scoped prompt for GitHub Copilot to review the repository for readability and maintainability without proposing unnecessary abstraction or feature expansion.

Copilot recommended two useful comments explaining:

- why the current payment is added to the previous-payment count
- that decision thresholds represent business-policy bands applied to additive rule scores

I rejected suggestions to remove all short function docstrings because I found some of them useful for quickly scanning the files.

ChatGPT also helped structure the README and this AI usage document. I checked the documented curl command by running it in the terminal and copied the service’s actual response into the README.

## Examples of challenging or correcting AI

### Reducing unnecessary complexity

The initial proposed project structure contained more files and layers than I could justify for a small time-boxed service. I simplified the starting structure and only separated responsibilities when the need became evident.

### Choosing SQLite over in-memory storage

ChatGPT initially recommended an in-memory list as the simplest persistence option. I chose SQLite because it remained lightweight and locally runnable while providing more robust querying, unique payment identifiers, and persistence across requests and restarts.

### Debugging the velocity implementation

When a manual request returned a server error after I changed its timestamp, the initial hypothesis was that the timestamp format might be invalid. I inspected the Uvicorn traceback, which showed that the actual error was:

`sqlite3.OperationalError: no such table: payments`

The fix was to ensure the database was initialised when the application started and then recreate the local database.

### Managing dependencies and test execution

When pytest could not import FastAPI, the terminal appeared to show an active virtual environment. By checking `which python` and `which pytest`, I found that Python was coming from the project environment while the standalone pytest command was using a global pyenv shim. I used `python -m pytest` to ensure tests ran with the correct interpreter rather than installing unnecessary duplicate dependencies.

## Validation approach

I validated AI-assisted work by:

- reading and understanding generated code before keeping it
- manually testing each rule through the API
- writing and running focused unit and API tests
- testing stateful velocity behaviour across repeated requests
- checking unhappy paths such as duplicate IDs and invalid amounts
- running the exact curl command documented in the README
- reviewing the complete repository for readability before submission

## AI development principles

Throughout the task, I aimed to:

- keep the implementation simple and contained
- challenge suggestions that added complexity without clear value
- prefer clear naming and structure over unnecessary comments or abstraction
- validate generated code through tests and manual API requests
- prioritise working behaviour and clear documentation over optional frontend polish
- retain only AI-generated code that I could understand and explain

## Approximate time and impact

I spent ~ three hours on the task, including planning, implementation, testing, debugging, and documentation. AI assistance was used throughout rather than as a separate block of time.

Without AI, I would have spent considerably longer looking up unfamiliar FastAPI, Pydantic, SQLite, and pytest patterns. AI accelerated implementation and helped me understand new concepts as I encountered them, while my time was focused on defining behaviour, challenging scope, making design decisions, validating the implementation, and debugging the complete service.
