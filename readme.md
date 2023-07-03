# Conferva - Conference Management System

Conferva is a conference management system designed to streamline the process of organizing conferences and managing conference-related tasks.

## Getting Started

To run the project locally, follow these steps:

1. Navigate to a folder of your choice or create a new one in the file explorer where you want to clone the Git         repository.

2. Right-click and open the terminal while being in that folder.

3. Clone the Git repository by running the following command:
   `git clone '<repository-link>'`

4. Navigate to the project root folder (`Conferva`) using the `cd` command: `cd Conferva`

5. Install the virtual environment package: `py -m pip install --user virtualenv`

6. Create a new environment: `py -m venv myenv`

7. Activate the virtual environment:
- Using Git Bash:
  `
  source ./env/Scripts/activate
  `
- Using Command Prompt or PowerShell:
  `
  .\env\Scripts\activate
  `

8. Install all the required packages for the project: `pip install -r requirements.txt`

9. Create a PostgreSQL database in pgAdmin named conferva_db and set a password for it (e.g., 123).

10. Create a `.env` file in the project root folder (Conferva) and copy the contents from the `.env-sample` file into it. Fill in the values for the following fields:
 ```
 SECRET_KEY=django-insecure-svk*_lwz42j8)no8gub7i7a(&^s%4v=vc_v*ia8d%2zdl@24&8
 DEBUG=True

 # Database configuration
 DB_NAME=conferva_db
 DB_USER=postgres
 DB_PASSWORD=123
 DB_HOST=localhost

 # Email configuration
 EMAIL_HOST=smtp.gmail.com
 EMAIL_PORT=587
 EMAIL_HOST_USER=abc@gmail.com
 EMAIL_HOST_PASSWORD=
 ```

11. Run the migrations to set up the database:
 - `python manage.py makemigrations`
 - `python manage.py migrate`
 

12. Create a superuser for accessing the admin panel:
 `python manage.py createsuperuser`

13. Start the development server:
 `python manage.py runserver`

## Additional Commands

- To deactivate the virtual environment:
`deactivate`

- To create a new Django app:
`python manage.py startapp <app-name>`

- Useful Git commands for version control:
    - `git status`
    - `git add -A`
    - `git commit -m "Commit message"`
    - `git push origin main`


- To start a new Django project:
`django-admin startproject myproject`




