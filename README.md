<div id="top"></div>

<h3 align="center">Duo Spraying</h3>

  <p align="center">
    <a href="https://github.com/LukeLauterbach/DuoSpray">View Demo</a>
    ·
    <a href="https://github.com/LukeLauterbach/DuoSpray/issues">Report Bug</a>
    ·
    <a href="https://github.com/LukeLauterbach/DuoSpray/issues">Request Feature</a>
  </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
   <li>
      <a href="#getting-started">Usage</a>
      <ul>
        <li><a href="#installation">Options</a></li>
      </ul>
    </li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

This script will automatically run through a list of Google searches, in order to automate Google Dorks for pen testing engagements.

![Script Screenshot](https://github.com/LukeLauterbach/DuoSpray/blob/main/image.png?raw=true)

### Built With

* [Python](https://www.python.org/)
* [Selenium](https://www.selenium.dev/)
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Password spraying is an integral part of penetration testing. DUO's cloud-based SSO solution is growing increasingly popular, but few solutions exist for testing organizations using DUO SSO. This solution will perform a password spraying attack against a DUO SSO protal.

If DUO SSO is used as the identity provider for M365, the script will automatically pull the organization's SSO URL. Otherwise, a DUO SSO URL can be manually specified.

### Installation

1. Clone the repo
   ```shell
   git clone https://github.com/LukeLauterbach/Google-Dorking-Automation.git
   ```
2. Install the dependencies
   ```shell
   git install -r requirements.txt
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

## Usage

```shell
python3 duospray.py [OPTIONAL ARGUMENTS] 
```

The script will look for files in the current directory named _userlist.txt_ and _passwords.txt_. Alternatively, files can be specified using `-u` and `-p`.

### Options
Option | Description
-|-
-u | Username File (Defaults to userlist.txt in The Current Directory)
-p | Password File (Defaults to passwords.txt in The Current Directory)
-U | Duo URL (Defaults to Grabbing URL from M365)
-d | Delay Between Unique Passwords
-dr | Delay Between Individual Password Attempts (For Added Stealth)
-db | Debug Mode


<p align="right">(<a href="#top">back to top</a>)</p>
