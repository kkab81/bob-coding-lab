# AI‑Assisted Development: A Hands‑On Lab with IBM Bob, Git & GitHub

## IBM Expert Labs - 30 Minute Hands-On Lab

**Duration:** 30-60 minutes
**Level:** Intermediate
**Audience:** Expert Labs Technical practitioners
**Version:** 1.03

## ⚠️ Notes - Guidance - Disclaimer

* We assume a basic level of technical proficiency, ideally including some experience with programming, Python, and VS Code at a beginner level or above. Practitioners are also expected to be comfortable with fundamental computer skills, such as installing software, navigating directory structures, and running scripts.
* If you are unsure how to install Git or Python for your operating system, you can ask IBM Bob for guidance.
* IBM Bob is an AI system, so its behaviour is "**not"** predictable. You may find that Bob performs very well at times and less effectively at others. Completing this lab should provide a good indication of Bob’s current programming capabilities.


* **This lab was tested on macOS Sequoia with Python 3.13.7. Running it on Windows or a different Python version may result in errors. That’s completely fine — this reflects real-world scenarios. If you run into issues, just ask Bob to help troubleshoot and fix them.**

***

## 🎯 Lab Objectives

By the end of this lab, you will:

* Use IBM Bob AI assistant to analyse, extend, and improve an existing Python application
* Apply core Git and GitHub Enterprise workflows (forking, cloning, branching, diffs, commits, and pull requests)
* Experience AI‑assisted code enhancement, documentation generation, review, and debugging
* Validate changes locally and push working code to GitHub Enterprise using a feature‑branch and PR‑based workflow

***

## 📋 Prerequisites

Before starting, ensure you have:

* ✅ GitHub Enterprise account (github.ibm.com)
* ✅ **Personal Access Token (PAT)** created for GitHub Enterprise
    * Go to: [https://github.ibm.com/settings/tokens](https://github.ibm.com/settings/tokens)
    * Click "Generate new token" drop down and select "**Generate new token (classic)**"
    * Enter a token name eg. boblab
    * **\*IMPORTANT\*** Select scopes: `repo` (full control of private repositories)
    * Generate New Token (green button at the end)
    * Copy and save the token securely (it will start: ***ghp\_very\_long\_string***) you'll need it later for `git clone`
* ✅ IBM Bob installed
* ✅ Git installed (https://git-scm.com/install) and configured locally (`git config --global user.name` and `user.email`)
    * Example:

        ```bash
        git config --global user.name "Alex Abderrazag"
        git config --global user.email "abderra@uk.ibm.com"
        ```
    * Windows users will have to close and re-open the terminal window after installing git
* ✅ Python 3.8+ installed (Download Python: [https://www.python.org/downloads](https://www.python.org/downloads))
* [optional] Watch 5min intro video: [https://ibm.box.com/s/ydd4p8e6kwp7ifvy44ivd0afzcq1ovm8](https://ibm.box.com/s/ydd4p8e6kwp7ifvy44ivd0afzcq1ovm8)

***

## 🚀 Phase 1: Setup & Initialization (5 minutes)

### Step 1.0: Fork the Sample Application from GitHub

**Forking** is the process whereby you create your own copy of a GitHub repository under your account, allowing you to make changes independently without affecting the original project.

Open [https://github.ibm.com/BOB-demo/bob-coding-lab.git](https://github.ibm.com/BOB-demo/bob-coding-lab.git) in your browser and in the top right - click on the fork button. This will open up a "**Create a new fork**" window, Accept the defaults and click on the green "**Create Fork**" Button.

**Note:** Forking is how open‑source and enterprise GitHub safely allow thousands of contributors without breaking the main repository. The starter application will be copied into your own personal GitHub space - **https://github.ibm.com/<*your GitHub userid*\>/bob\-coding\-lab\.git**

Your GitHub ***userid*** is located in the top left of the browser at [https://github.ibm.com](https://github.ibm.com).
Make a note of this repo URL eg: **https://github.ibm.com/<*your GitHub userid*\>/bob\-coding\-lab\.git\.** You are now the owner of a forked Python repo!

### Step 1.1: Clone the Sample Application (Starter Repository)

**Cloning** is the process whereby you copy a GitHub repo locally to your machine to start development.

Open a command line terminal and Clone the Sample Application. You'll be prompted to **Authenticate:**

* **Username:** Your GitHub Enterprise username (e.g., `abderra`)
* **Password:** Use your **Personal Access Token** (NOT your IBM password - [hint] **ghp\_very\_long\_string)**

```bash
git clone https://github.ibm.com/<your GitHub id>/bob-coding-lab.git
cd bob-coding-lab
```

**Notes:**
This is the application project repository.
Cloning a public repo doesn't require credentials.
Do not close the command line window - you'll be working in this terminal throughout the lab.

**Optional - Tip:** To avoid entering credentials repeatedly, you can cache them:

```bash
mac # git config --global credential.helper osxkeychain
linux # git config --global credential.helper manager -OR- git config --global credential.helper store
windows # git config --global credential.helper manager
```

### Step 1.2: Create Your Development Branch

Create a branch using your email address **(in lowercase**) for easy tracking:

```bash
git checkout -b dev/your.email@ibm.com

[Note: use lowercase - it's just generally easier! Although it doesn't really matter]
```

**Example:**

```bash
git checkout -b dev/john.smith@ibm.com
```

**💡 Why this naming?** This allows EL to easily verify lab completion by checking branch names.

### Step 1.3: Explore the Project with IBM Bob

Open the Python starter application in IBM Bob **(File → Open Folder**) and select the folder of your local clone (i.e. **the project directory on your machine**).
Then switch to ASK mode and ask IBM Bob:

**Prompt to IBM Bob:**

```
Analyze this World Time application. Explain:
1. What the application does
2. The main features in app.py
3. How weather data is handled via weather.py
4. The API endpoints available
```

**Flash/Python/HTML code Bob will analyse:**

* `app.py` \- Complete Flask world time application \(841 lines\)
* `weather.py` \- Weather cache builder script \(177 lines\)
* `requirements.txt` \- Python dependencies
* `templates/index.html` \- Full HTML template with UI \(5900\+ lines\)
* `.gitignore` \- Git ignore rules
* `README.md` \- Project documentation
* `SETUP.md` \- Setup instructions

**What You'll Learn:**
This is a fully functional world clock showing 50+ cities with weather, moon phases, holidays, and meeting planner features. The `weather.py` script fetches weather data from Open-Meteo API and caches it for 24 hours.

### Step 1.4: Setting up and starting the sample Python application: Create and Activate Virtual Environment

From the command line terminal, Create a Python virtual environment:

```bash
Mac/Linux: python3 -m venv venv
Windows: python -m venv venv
```

Python virtual environments let you isolate project dependencies so each project can use exactly the libraries and versions it needs without conflicts. That isolation makes your development setup reproducible, safer to upgrade, and far easier to debug — which is why they’re a must for serious Python work.

Activate the virtual environment:

* **macOS/Linux:**

    ```bash
    source venv/bin/activate
    ```
* **Windows:**

    ```bash
    venv\Scripts\activate
    ```

### Step 1.5: Install Python Dependencies

Python dependencies are third‑party libraries that the application relies on to run correctly, and they are defined in the requirements.txt file.

```bash
pip install -r requirements.txt

[Note: You may encounter version issues depending on your Python setup. If so, just ask Bob to resolve them]
```

### Step 1.6: Run the Application Locally

First, fetch weather data (recommended):
**Note:** Windows uses just use **python not python3**

```bash
python3 weather.py
```

Then start the Python application:

```bash
python3 app.py
```

Navigate to [`http://localhost:5001`](http://localhost:5001) in your browser.

Explore the application.

<img width="1299" alt="image" src="https://github.ibm.com/user-attachments/assets/ef7508e6-19a3-4d1a-823d-0def9cddfad1" />

***

**✅ Checkpoint:** You should have the project cloned, dependencies installed, app up and running. IBM Bob is now ready to assist.

***

## 💻 Phase 2: Code Enhancement with IBM Bob (12 minutes)

### Task 2.1: Add a New City (4 minutes)

**Objective:** Use IBM Bob in "CODE" mode to add support for a new city in a timezone gap.

**Prompt to IBM Bob:**

```
Add support for "Hanoi" (Vietnam) to the CITIES dictionary in app.py.
Include timezone 'Asia/Ho_Chi_Minh', latitude 21.0285, longitude 105.8542.
Also add it to CITY_TO_COUNTRY mapping with country code 'VN'.
This fills the UTC+7 timezone gap in our world clock.
```

**What IBM Bob Will Do:**

* Locate the CITIES dictionary in app.py
* Add the new city entry with correct format
* Update CITY\_TO\_COUNTRY mapping

**After IBM Bob Makes Changes:** from your command line window

```bash
git add .
git commit -m "feat: add Hanoi to fill UTC+7 timezone gap"
```

**💡 Best Practice:** Atomic commits with descriptive messages using conventional commit format.

***

### Task 2.2: Add API Documentation (4 minutes)

**Objective:** Use IBM Bob to create API documentation. Remain in "CODE" mode.

**Prompt to IBM Bob:**

```
Create a new file called API.md that documents all the API endpoints in app.py.
Include endpoint URLs, parameters, response formats, and example requests.
Make it clear and well-formatted for developers.
```

**What IBM Bob Will Do:**

* Analyze all Flask routes in app.py
* Generate comprehensive API documentation
* Create properly formatted markdown file

**After IBM Bob Creates the File:**

```bash
git add API.md
git commit -m "docs: add API endpoint documentation"
```

***

### Task 2.3: Add Dark Theme Support (4 minutes)

**Objective:** Enhance the UI with a dark theme toggle.

**Prompt to IBM Bob:**

```
Add dark theme support to templates/index.html:
- Create CSS variables for light and dark color schemes
- Add a theme toggle button in the UI
- Store user preference in localStorage
- Apply dark theme with smooth transitions
- Ensure all elements (cards, text, backgrounds) adapt properly
```

**What IBM Bob Will Do:**

* Add CSS variables for theming
* Create dark theme color palette
* Implement toggle functionality with JavaScript
* Add localStorage persistence

**After IBM Bob Updates the File:**

```bash
git add .
git commit -m "feat: add dark theme support with toggle"
```

**✅ Checkpoint:** You should have 3 commits on your feature branch with meaningful enhancements.

***

## 🧪 Phase 3: Testing & Debugging (6 minutes)

### Step 3.1: Re-start the Python Application

### ⏹️ Stop and Restart the Application

Quit the currently running application:

* **Windows / Linux: Ctrl + C**
* **macOS:** ⌘ **Command** + **C**

```bash
python3 app.py
```

Navigate again to [`http://localhost:5001`](http://localhost:5001) in your browser.
**Note:** You will additionally have to force reload the app to avoid browser cache issues. examples:

* **Force Reload (Ignore Browser Cache):**
    * **macOS – Safari:**
        ⌘ **Command** + ⌥ **Option** + **R**
    * **macOS – Chrome/FireFix:**
        ⌘ **Command** + ⇧ **Shift** + **R**
    * **Windows / Linux – Chrome & Firefox:**
        **Ctrl** + ⇧ **Shift** + **R**
<br>
        Ask Bob if you experience issues.

### Step 3.2: Test Your Changes

Test the enhancements you made to ensure the application behaves as expected.

### Note:

As you test, **do not worry if some of IBM Bob’s generated enhancements do not work perfectly on the first attempt**. This lab is **not an assessment of Bob proficiency**, but an opportunity to experience how AI can assist—and sometimes challenge—real‑world development workflows.

* Verify Hanoi appears in the city list and shows UTC+7 timezone. Hint - "Select timezones icon (first icon in the header and select Hanoi - then save"
* Check the API.md documentation is clear and comprehensive
* Test the dark theme toggle - switch between light and dark modes
* Verify theme preference persists after page reload

## NOTE: You may proceed to Phase 4. Steps 3.3 - 3.5 are optional (depending on time and experience!)

### Step 3.3: Use IBM Bob for Debugging

**Scenario:** You notice the meeting planner doesn't handle edge cases well.

**Prompt to IBM Bob:**

```
Review the meeting_planner function in app.py and identify any edge cases
or potential bugs. Suggest improvements for handling.
```

**What IBM Bob Will Do:**

* Analyze the code for edge cases
* Suggest improvements / Code fixes

### Step 3.4: Apply IBM Bob's Suggestions

Implement the improvements IBM Bob suggests.

**Commit the Fix:**

```bash
git add .
git commit -m "fix: improve meeting planner edge case handling"
```

### Step 3.5: Code Quality Review

**Prompt to IBM Bob:**

```
Review my recent commits for:
- Code quality 
- Security issues
- Potential bugs
```

Optional\* Address any issues IBM Bob identifies.

**✅ Checkpoint:** Application runs without errors, your enhancements work correctly, and code has been reviewed.

***

## 🔄 Phase 4: Git Workflow & GitHub Push (5 minutes)

### Step 4.1: Check Your Work Status

From your command line window, View what files you've modified:

```bash
git status
```

### Step 4.2: Review Your Commit History

See all your commits:

```bash
git log --oneline
```

View detailed commit history:

```bash
git log --graph --decorate --oneline
```

### Step 4.3: Compare Your Changes

Compare your branch to main:

```bash
git diff main..dev/your.email@ibm.com
```

View changes in a specific file:

```bash
git diff main app.py
```

### Step 4.4: Generate Commit Summary with IBM Bob

**Prompt to IBM Bob:**

```
Review my git commit history and generate a summary of all changes I made.
Include:
- Summary of enhancements
- Files modified
- Key improvements
- Testing notes
```

**IBM Bob will generate a comprehensive summary of your work.**

### Step 4.5: Push Your Branch to GitHub

Push your development branch:

```bash
git push origin dev/your.email@ibm.com
```

**Note:** If this is your first push, you may need to set upstream:

```bash
git push -u origin dev/your.email@ibm.com
```

### Step 4.6: Verify Your Push

Check your branch exists on GitHub:

```bash
git branch -r | grep dev/your.emailOr visit: https://github.ibm.com/<your GitHub userid>/bob-coding-lab/branches
```

### Step 4.7: Final Step - Share Your Completed Work via a Pull Request

You will now instruct GitHub to compare your development branch against the original repository and formally request that your changes be reviewed and merged. No code is merged automatically—this step creates visibility and allows the Expert Labs team to review your work.
This pull‑request‑based workflow mirrors how real open‑source and enterprise development projects collaborate and review changes in practice.

Go to your cloned Repo on GitHub: **https://github.ibm.com/\<your GitHub userid>/bob-coding-lab** \- you will see a line similar to that below\. This branch is X commits ahead of the original master repo: **Bob-demo/bob-coding-lab:main.**

##### \*Important\* Your main branch will be selected by default! Make sure you 1. Select your dev/*\<email>* branch and 2. Press "**Contribute**" then select "**Open Pull Request**"

<img width="1179" alt="image" src="https://github.ibm.com/user-attachments/assets/ede9c3f4-0209-44bd-ab20-cbf75df454d3" />

On the next screen: **Comparing changes** \- accept the defaults and press **"Create Pull Request".**

You see a PR confirmation header like the one below - stop there.

**✅ Checkpoint:** A Pull request has been created to merge your updates to the master project. At this point your work is done and visible to the EL team.

<img width="1161" alt="image" src="https://github.ibm.com/user-attachments/assets/d21994c9-08d1-4db5-8f82-3044c47382fb" />

***

## 👏 Congratulations!

You've completed the AI-Assisted Development with Bob & GitHub lab. You now have hands-on experience using AI to accelerate development while maintaining professional Git workflows.

**Next Steps:**

* Apply these techniques in your daily work
* Share Bob best practices with your team
* Explore advanced Bob features in your projects

***

## 🏆 Success Criteria

You've successfully completed the lab if you:

* ✅ Created X+ meaningful Git commits with conventional commit messages
* ✅ Pushed your `dev/your.email@ibm.com` branch to GitHub Enterprise
* ✅ Used essential Git commands (status, log, diff, push)
* ✅ Used IBM Bob for at least 3 different tasks (enhancement, debugging, review)
* ✅ Application runs with your enhancements working correctly
* ✅ Expert Labs can see your branch on GitHub

***

## 🎓 Reflection

**IBM Bob Best Practices:**

* ✅ **Iterative prompts** \- Enhance features step\-by\-step with clear instructions
* ✅ **Context awareness** \- IBM Bob understands your project structure and dependencies
* ✅ **Code review** \- Use IBM Bob to catch issues before pushing
* ✅ **Documentation** \- Generate PR descriptions and API docs automatically
* ✅ **Verification** \- Always test IBM Bob's code\, especially for security\-critical features

**Git Workflow Reinforced:**

* ✅ Feature branching strategy keeps main stable
* ✅ Atomic, meaningful commits tell a story
* ✅ PR-based collaboration enables code review
* ✅ AI-generated descriptions improve communication

***

## 🚀 **Advanced** Extension Challenges (If you wish to go further!)\*\*

1. **Performance Optimisation**
    * Ask IBM Bob to review `app.py` for potential performance bottlenecks and recommend appropriate caching strategies.
    * Implement the suggested improvements and validate the impact.
2. **Expose a REST API (Developer Integration)**
    * Extend the application by adding REST API endpoints to enable programmatic access to its core functionality.
3. **Build an MCP Server Integration**
    * Ask Bob to create an MCP server (e.g. **`pytime` MCP**) that consumes the REST API.
    * Use this MCP to enable natural-language queries such as:
        * *“What’s the weather like in London?”*
        * *“What’s the best 1‑hour meeting time across London, New York, and Singapore?”*

***

## 📚 Additional Resources

* **Git Best Practices:** https://www.w3schools.com/git/git\_best\_practices.asp?remote=github
* **Open-Meteo API:** https://open-meteo.com/
* **Flask Documentation:** https://flask.palletsprojects.com/
* **pytz Documentation:** https://pythonhosted.org/pytz/

***

## 🆘 Troubleshooting

### Common Issues:

**Issue:** Weather data not showing

* **Solution:** Run `python3 weather.py` to fetch weather data, then restart app

**Issue:** Git push authentication failed

* **Solution:**
    * Verify you're using your Personal Access Token (PAT), not your IBM password
    * Check token has `repo` scope enabled
    * Generate a new token if needed: https://github.ibm.com/settings/tokens

**Issue:** Import errors

* **Solution:** Ensure virtual environment is activated: `source venv/bin/activate`

**Issue:** Port 5001 already in use

* **Solution:** Kill existing process: `lsof -ti:5001 | xargs kill -9` or change port in app.py
