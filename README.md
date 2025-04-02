# python-selenium-browserstack-assignment
Steps to run the python selenium test on browserstack - assignment_browserstack.py

## Prerequisite
```
python3 should be installed
```

## Setup
* Clone the repo
```
git clone https://github.com/sush24een/python-selenium-browserstack.git
``` 
* Install packages through requirements.txt
```
pip3 install -r requirements.txt
```

## Set BrowserStack Credentials
* Add your BrowserStack username and access key in the `browserstack.yml` config fle.
* You can also export them as environment variables, `BROWSERSTACK_USERNAME` and `BROWSERSTACK_ACCESS_KEY`:

  #### For Linux/MacOS
    ```
    export BROWSERSTACK_USERNAME=<browserstack-username>
    export BROWSERSTACK_ACCESS_KEY=<browserstack-access-key>
    ```
  #### For Windows
    ```
    setx BROWSERSTACK_USERNAME=<browserstack-username>
    setx BROWSERSTACK_ACCESS_KEY=<browserstack-access-key>
    ```

## Running tests
* Run sample test:
  - To run the assignment test platforms defined in the `browserstack.yml` file, run:
    ```
    browserstack-sdk ./tests/assignment_browserstack.py
    ``` 
## Notes - future scopes and improvements
* Use explicit waits before interacting with elements for better synchronization.
* Optimize navigation by reducing unnecessary page reloads (e.g., minimize driver.back() calls).
* Implement better handling for paywalled articles.
* Enhance retry mechanisms for failed requests or missing elements.
* Store extracted data in a structured format (CSV/JSON) for better usability.

