#!flask/bin/python

from flask import Flask, jsonify, abort, request, make_response
import json
import sys
import os
import os.path
from pathlib import Path
import tarfile
from zipfile import ZipFile

app = Flask(__name__)

config_file = "artstore.json"
projects_file = "projects.json"

def load_config(file_name):
    with open(file_name, 'r') as config_file:
        data = config_file.read()

    try:
        new_config = json.loads(data)
        # Json parsed successfully, now validate
        # if base_path directory doesn't exist then try to create it
        base_path = new_config['base_path']
        if not os.path.isdir(base_path):
            try:
                p = Path(base_path)
                p.mkdir(parents=True)
            except BaseException as e:
                print("Failed to create directory %s: %s" % (base_path, e))
                sys.exit(1)
        temp_path = new_config['temp_path']
        if not os.path.isdir(temp_path):
            try:
                p = Path(temp_path)
                p.mkdir(parents = True)
            except BaseException as e:
                print("Failed to create temp directory %s: %s" % (temp_path,e))
                sys.exit(1)
        # Update the config
        global config
        config = new_config
        print("Read config from %s" % file_name)
        
    except ValueError:
        print("Failed to load config from %s" % file_name)
        sys.exit(1)

def load_projects(file_name):
    with open(file_name, 'r') as project_file:
        data = project_file.read()

    try:
        new_projects = json.loads(data)
        # parsed json successfully, now validate it
        global projects
        projects = new_projects
        # ensure that project directories exist
        for project_name in projects:
            create_project_dirs(project_name)
        print("Read projects from %s" % file_name)
    except ValueError:
        print('Failed to load projects from %s' % file_name)
        projects = {}

def save_projects(file_name):
    with open(file_name, 'w') as project_file:
        project_file.write(json.dumps(projects, indent=4))

def create_project_dirs(project_name):
    project = projects[project_name]
    top = Path(os.path.join(config['base_path'],project['path']))
    try:
        top.mkdir(parents = True)
    except:
        pass
    items = project['items']
    for item_name in items:
        item = items[item_name]
        dir = Path(os.path.join(config['base_path'],project['path'],item['dir']))
        try:
            dir.mkdir(parents = True)
        except:
            pass

def handle_html(project_name,item_name,file_name):
    project = projects[project_name]
    item = project['items'][item_name]
    src_path = Path(os.path.join(config['temp_path'],file_name))
    dest_path = Path(os.path.join(config['base_path'],project['path'],item['dir'],file_name))
    try:
        dest_path.unlink(missing_ok = True)
    except BaseException as e:
        print("Exception while unlinking %s: %s" %(dest_path,e))
        return make_response(jsonify({'error': 'Error removing file ' + dest_path}),400)
    try:
        src_path.rename(dest_path)
        return make_response(jsonify({'success': 'Updated item ' + item_name + ' in project ' + project_name}),200)
    except BaseException as e:
        print("Exception while renaming %s to %s: %s" %(src_path,dest_path,e))
        return make_response(jsonify({'error': 'Error moving file ' + dest_path}),400)

def handle_tgz(project_name,item_name,file_name):
    project = projects[project_name]
    item = project['items'][item_name]
    src_path = Path(os.path.join(config['temp_path'],file_name))
    dest_path = Path(os.path.join(config['base_path'],project['path'],item['dir']))
    # Clear out current destination directory contents
    for f in dest_path.glob('*'):
        try:
            f.unlink()
        except:
            return make_response(jsonify({'error': 'Error removing files in' + dest_path}),400)
    # Extract tarball to destination directory
    file = tarfile.open(src_path)
    file.extractall(dest_path)
    file.close
    # Cleanup: delete tarball
    src_path.unlink()
    return make_response(jsonify({'success': 'Updated item ' + item_name + ' in project ' + project_name}),200)

def handle_zip(project_name,item_name,file_name):
    project = projects[project_name]
    item = project['items'][item_name]
    src_path = Path(os.path.join(config['temp_path'],file_name))
    dest_path = Path(os.path.join(config['base_path'],project['path'],item['dir']))
    # Clear out current destination directory contents
    for f in dest_path.glob('*'):
        try:
            f.unlink()
        except:
            return make_response(jsonify({'error': 'Error removing files in' + dest_path}),400)
    # Extract zip file to destination directory
    with ZipFile(src_path) as zipObj:
        zipObj.extractall(dest_path)
    return make_response(jsonify({'success': 'Updated item ' + item_name + ' in project ' + project_name}),200)

@ app.errorhandler(400)
def invalid_data(error):
    return make_response(jsonify({'error': 'Invalid content type'}))

@ app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Project Not found'}), 404)

@ app.route('/artstore', methods=['GET'])
def get_projects():
    return jsonify({'projects': list(projects.keys())})

@ app.route('/artstore/<project_name>', methods=['POST'])
def add_project(project_name):
    if project_name in projects:
        return make_response(jsonify({'error': 'Project already exists'}), 400)

    content = request.get_json()
    if 'name' in content and 'path' in content and 'items' in content:
        items = content['items']
        for item in items:
            it = items[item]
            if 'name' in it and 'dir' in it and 'type' in it:
                # Item definition is valid
                pass
            else:
                return make_response(jsonify({'error': 'Item ' + item + ' missing required keywords'}), 400)
        # Project definition is valid
        projects[project_name] = content
        create_project_dirs(project_name)
        save_projects(projects_file)
        return make_response(jsonify({'success': 'project ' + project_name + ' added'}), 200)
    else:
        return make_response(jsonify({'error': 'Project ' + project_name + ' missing required keywords'}), 400)


@ app.route('/artstore/<project>', methods=['DELETE'])
def del_project(project):
    if project in projects:
        del projects[project]
        save_projects(projects_file)
        return make_response(jsonify({'success': 'project ' + project + 'deleted'}), 200)
    else:
        return make_response(jsonify({'error': 'Project ' + project + ' does not exist'}), 404)


@ app.route('/artstore/<project>', methods=['GET'])
def get_project(project):
    if project in projects:
        return make_response(jsonify({project: projects[project]}), 200)
    else:
        return make_response(jsonify({'error': 'Project ' + project + ' does not exit'}), 404)

@ app.route('/artstore/<project_name>/<item_name>', methods=['POST'])
def put_item(project_name, item_name):
    if project_name in projects:
        project = projects[project_name]
        if item_name in project["items"]:
            item = project["items"][item_name]
            print("request.headers=%s" % request.headers)
            print("request.files=%s" % request.files)
            if "multipart/form-data" in request.headers["Content-Type"]:
                form_dict = request.form.to_dict()
                if 'item' in request.files:
                    file = request.files['item']
                    if file.filename != '':
                        file_name = os.path.join(config["temp_path"],file.filename)
                        file.save(file_name)
                        print("Wrote file %s" % file_name)
                        # TODO: delegate based on item type
                        if item['type'] == "html":
                            return handle_html(project_name,item_name,file.filename)
                        elif item['type'] == "tgz":
                            return handle_tgz(project_name,item_name,file.filename)
                        elif item['type'] == "zip":
                            return handle_zip(project_name,item_name,file.filename)
                        elif item['type'] == "collection":
                            # TODO: support collection
                            return make_response(jsonify({'success': 'Updated item ' + item_name + ' in project ' + project_name}),200)
                    else:
                        return make_response(jsonify({'error': 'Filename not specified in multipart/form data'}),400)
                else:
                    return make_response(jsonify({'error': 'item missing in multipart/form data'}))
            else:
                return make_response(jsonify({'error': 'Unexpected Content-Type:' + request.headers["Content-Type"]}),400)
        else:
            return make_response(jsonify({'error': 'Item ' + item_name + ' does not exist in project ' + project_name}),404)
    else:
        return make_response(jsonify({'error': 'Project ' + project_name + ' does not exist'}),404)

if __name__ == '__main__':
    load_config('artstore.json')
    load_projects('projects.json')
    app.run(debug=True)
