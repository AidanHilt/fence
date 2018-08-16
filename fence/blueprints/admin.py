"""
Blueprints for administation of the userdatamodel database and the storage
solutions. Operations here assume the underlying operations in the interface
will maintain coherence between both systems.
"""

import functools

import flask
from flask import jsonify, request
from flask_sqlalchemy_session import current_session

from fence.auth import require_auth, require_admin
from fence.resources import admin


blueprint = flask.Blueprint('admin', __name__)


def debug_log(function):
    """Output debug information to the logger for a function call."""
    argument_names = list(function.func_code.co_varnames)

    @functools.wraps(function)
    def write_log(*args, **kwargs):
        argument_values = (
            '{} = {}'.format(arg, value)
            for arg, value in zip(argument_names, args) + kwargs.items()
        )
        msg = function.func_name + '\n\t' + '\n\t'.join(argument_values)
        flask.current_app.logger.debug(msg)
        return function(*args, **kwargs)

    return write_log


#### USERS ####


@blueprint.route('/user/<username>', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def get_user(username):
    """
    Get the information of a user from our userdatamodel database

    Returns a json object
    """
    return jsonify(admin.get_user_info(current_session, username))


@blueprint.route('/user', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def get_all_users():
    """
    Retrieve the information regarding the buckets created within a project.
    Returns a json object.
    """
    return jsonify(admin.get_all_users(current_session))


@blueprint.route('/user', methods=['POST'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def create_user():
    """
    Create a user on the userdatamodel database

    Returns a json object
    """
    username = request.get_json().get('name', None)
    role = request.get_json().get('role', None)
    email = request.get_json().get('email', None)
    return jsonify(admin.create_user(current_session, username, role, email))


@blueprint.route('/user/<username>', methods=['PUT'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def update_user(username):
    """
    Create a user on the userdatamodel database

    Returns a json object
    """
    name = request.get_json().get('name', None)
    role = request.get_json().get('role', None)
    email = request.get_json().get('email', None)
    return jsonify(
        admin.update_user(current_session, username, role, email, name)
    )


@blueprint.route('/user/<username>', methods=['DELETE'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def delete_user(username):
    """
    Remove the user from the userdatamodel database and all associated storage
    solutions.

    Returns json object
    """
    response = jsonify(admin.delete_user(current_session, username))
    return response


@blueprint.route('/user/<username>/groups', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def get_user_groups(username):
    """
    Get the information of a user from our userdatamodel database.

    Returns a json object
    """
    return jsonify(admin.get_user_groups(current_session, username))


@blueprint.route('/user/<username>/groups', methods=['PUT'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def add_user_to_groups(username):
    """
    Create a user to group relationship in the database

    Returns a json object
    """
    groups = request.get_json().get('groups', [])
    return jsonify(
        admin.add_user_to_groups(current_session, username, groups=groups)
    )


@blueprint.route('/user/<username>/groups', methods=['DELETE'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def remove_user_from_groups(username):
    """
    Create a user to group relationship in the database

    Returns a json object
    """
    groups = request.get_json().get('groups', [])
    return jsonify(
        admin.remove_user_from_groups(current_session, username, groups=groups)
    )


@blueprint.route('/user/<username>/projects', methods=['DELETE'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def remove_user_from_projects(username):
    """
    Create a user to group relationship in the database

    Returns a json object
    """
    projects = request.get_json().get('projects', [])
    return jsonify(
        admin.remove_user_from_projects(current_session, username, projects)
    )


@blueprint.route('/user/<username>/projects', methods=['PUT'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def add_user_to_projects(username):
    """
    Create a user to project relationship on the database and add the access to
    the the object store associated with it

    Returns a json object
    """
    projects = request.get_json().get('projects', [])
    return jsonify(
        admin.add_user_to_projects(
            current_session, username, projects=projects
        )
    )


#### PROJECTS ####


@blueprint.route('/projects/<projectname>', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def get_project(projectname):
    """
    Get the information related to a project
    from the userdatamodel database
    Returns a json object
    """
    return jsonify(admin.get_project_info(current_session, projectname))


@blueprint.route('/projects', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def get_all_projects():
    """
    Get the information related to a project
    from the userdatamodel database
    Returns a json object
    """
    return jsonify(admin.get_all_projects(current_session))


@blueprint.route('/projects/<projectname>', methods=['POST'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def create_project(projectname):
    """
    Create a new project on the specified storage
    Returns a json object
    """
    auth_id = request.get_json().get('auth_id')
    storage_accesses = request.get_json().get('storage_accesses', [])
    response = jsonify(
        admin.create_project(
            current_session,
            projectname,
            auth_id,
            storage_accesses
        )
    )
    return response


@blueprint.route('/projects/<projectname>', methods=['DELETE'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def delete_project(projectname):
    """
    Remove project. No Buckets should be associated with it.
    Returns a json object.
    """
    response = jsonify(admin.delete_project(current_session, projectname))
    return response


@blueprint.route('/groups/<groupname>/projects', methods=['DELETE'])
@require_admin
@require_auth(aud={'openid'})
@debug_log
def remove_projects_from_group(groupname):
    """
    Create a user to group relationship in the database
    Returns a json object
    """
    projects = request.get_json().get('projects', [])
    return jsonify(
        admin.remove_projects_from_group(current_session,groupname, projects)
    )


@blueprint.route('/projects/<projectname>/groups', methods=['PUT'])
@require_admin
@require_auth(aud={'openid'})
def add_project_to_groups(projectname):
    """
    Create a user to group relationship in the database
    Returns a json object
    """
    groups = request.get_json().get('groups', [])
    return jsonify(
        admin.add_project_to_groups(current_session, projectname, groups=groups)
    )


@blueprint.route('/projects/<projectname>/bucket/<bucketname>', methods=['POST'])
@require_admin
@require_auth(aud={'openid'})
def create_bucket_in_project(projectname, bucketname):
    """
    Create a bucket in the selected project.
    Returns a json object.
    """
    providername = request.get_json().get('provider')
    response = jsonify(
        admin.create_bucket_on_project(
            current_session,
            projectname,
            bucketname,
            providername
        )
    )
    return response


@blueprint.route(
    '/projects/<projectname>/bucket/<bucketname>',
    methods=['DELETE']
)
@require_admin
@require_auth(aud={'openid'})
def delete_bucket_from_project(projectname, bucketname):
    """
    Delete a bucket from the selected project, both
    in the userdatamodel database and in the storage client
    associated with that bucket.
    Returns a json object.
    """
    return jsonify(
        admin.delete_bucket_on_project(
            current_session, projectname, bucketname
        )
    )


@blueprint.route('/projects/<projectname>/bucket', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
def list_buckets_from_project(projectname):
    """
    Retrieve the information regarding the buckets created within a project.

    Returns a json object.
    """
    response = jsonify(
        admin.list_buckets_on_project_by_name(current_session, projectname)
    )
    return response


#### GROUPS ####


@blueprint.route('/groups/<groupname>', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
def get_group_info(groupname):
    """
    Retrieve the information regarding the
    buckets created within a project.
    Returns a json object.
    """
    return jsonify(admin.get_group_info(current_session, groupname))


@blueprint.route('/groups', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
def get_all_groups():
    """
    Retrieve the information regarding the
    buckets created within a project.
    Returns a json object.
    """
    return jsonify(admin.get_all_groups(current_session))


@blueprint.route('/groups/<groupname>/users', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
def get_group_users(groupname):
    """
    Retrieve the information regarding the
    buckets created within a project.
    Returns a json object.
    """
    return jsonify(admin.get_group_users(current_session, groupname))


@blueprint.route('/groups', methods=['POST'])
@require_admin
@require_auth(aud={'openid'})
def create_group():
    """
    Retrieve the information regarding the
    buckets created within a project.
    Returns a json object.
    """
    groupname = request.get_json().get('name')
    description = request.get_json().get('description')
    grp = admin.create_group(current_session, groupname, description)
    if grp:
        response = admin.get_group_info(current_session, groupname)
    else:
        response = {'result': 'group creation failed'}
    response = jsonify(response)
    return response


@blueprint.route('/groups/<groupname>', methods=['PUT'])
@require_admin
@require_auth(aud={'openid'})
def update_group(groupname):
    """
    Retrieve the information regarding the
    buckets created within a project.
    Returns a json object.
    """
    name = request.get_json().get('name', None)
    description = request.get_json().get('description', None)
    response = jsonify(admin.update_group(current_session, groupname, description, name))
    return response


@blueprint.route('/groups/<groupname>', methods=['DELETE'])
@require_admin
@require_auth(aud={'openid'})
def delete_group(groupname):
    """
    Retrieve the information regarding the
    buckets created within a project.
    Returns a json object.
    """
    response = jsonify(admin.delete_group(current_session, groupname))
    return response


@blueprint.route('/groups/<groupname>/projects', methods=['PUT'])
@require_admin
@require_auth(aud={'openid'})
def add_projects_to_group(groupname):
    """
    Create a user to group relationship in the database
    Returns a json object
    """
    projects = request.get_json().get('projects', [])
    response = jsonify(
        admin.add_projects_to_group(current_session, groupname, projects)
    )
    return response


@blueprint.route('/groups/<groupname>/projects', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
def get_group_projects(groupname):
    """
    Create a user to group relationship in the database
    Returns a json object
    """
    values = admin.get_group_projects(current_session, groupname)
    return jsonify({"projects": values})


#### CLOUD PROVIDER ####


@blueprint.route('/cloud_provider/<providername>', methods=['GET'])
@require_admin
@require_auth(aud={'openid'})
def get_cloud_provider(providername):
    """
    Retriev the information related to a cloud provider
    Returns a json object.
    """
    return jsonify(admin.get_provider(current_session, providername))


@blueprint.route('/cloud_provider/<providername>', methods=['POST'])
@require_admin
@require_auth(aud={'openid'})
def create_cloud_provider(providername):
    """
    Create a cloud provider.
    Returns a json object
    """
    backend_name = request.get_json().get('backend')
    service_name = request.get_json().get('service')
    response = jsonify(
        admin.create_provider(
            current_session,
            providername,
            backend=backend_name,
            service=service_name
        )
    )
    return response


@blueprint.route('/cloud_provider/<providername>', methods=['DELETE'])
@require_admin
@require_auth(aud={'openid'})
def delete_cloud_provider(providername):
    """
    Deletes a cloud provider from the userdatamodel
    All projects associated with it should be deassociated
    or removed.
    Returns a json object.
    """
    response = jsonify(admin.delete_provider(current_session, providername))
    return response
