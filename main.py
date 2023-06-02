from flask import Flask, render_template, request, redirect, url_for, abort, session
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Disable template caching

# Rest of the code...

# Dictionary to store username and password combinations
users = {
    "admin": "password123",
    "admin2": "password1234"
}

# Check if the user is authenticated
def is_authenticated():
    return 'username' in session

# Check if username and password are valid
def check_auth(username, password):
    return username in users and users[username] == password

# Return the authentication request
def authenticate_request():
    return abort(401, "Authentication required.")

def create_blog(blog_name):
    blog_html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{}</title>
    </head>
    <body>
        <h1>{}</h1>
        <!-- Your blog content goes here -->
    </body>
    </html>
    '''.format(blog_name, blog_name)

    with open('templates/blogs/{}.html'.format(blog_name), 'w') as file:
        file.write(blog_html)

    # Set the blog owner in the session
    session['blog_owner'] = session['username']

# Index route with blog creation form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        blog_name = request.form['blog_name']
        if not is_authenticated():
            return authenticate_request()
        create_blog(blog_name)
        return redirect(url_for('blog', blog_name=blog_name))
    return render_template('index.html')



# Route to view the blog
@app.route('/blog/<blog_name>', methods=['GET'])
def blog(blog_name):
    if not is_authenticated():
        return authenticate_request()
    return render_template('blogs/{}.html'.format(blog_name))

@app.route('/blog/<blog_name>/edit', methods=['GET', 'POST'])
def edit_blog(blog_name):
    if not is_authenticated():
        return authenticate_request()

    # Check if the blog file exists
    blog_file_path = 'templates/blogs/{}.html'.format(blog_name)
    if not os.path.exists(blog_file_path):
        abort(404, "Blog does not exist.")

    # Check if the currently logged-in user is the owner of the blog
    if 'username' not in session or session['username'] != session['blog_owner']:
        abort(403, "Unauthorized access.")

    if request.method == 'POST':
        new_content = request.form['content']
        update_blog(blog_name, new_content)
        return redirect(url_for('blog', blog_name=blog_name))
    else:
        # Read the existing content of the blog file
        with open(blog_file_path, 'r') as file:
            content = file.read()
        return render_template('edit_blog.html', blog_name=blog_name, content=content)





# Update the content of the blog file
def update_blog(blog_name, new_content):
    blog_file_path = 'templates/blogs/{}.html'.format(blog_name)
    with open(blog_file_path, 'w') as file:
        file.write(new_content)
    return redirect(url_for('blog', blog_name=blog_name))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_auth(username, password):
            session['username'] = username
            session['blog_owner'] = username  # Set the blog owner in the session
            return redirect(url_for('index'))
        else:
            return abort(401, "Invalid username or password.")
    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run('0.0.0.0', port=81)
