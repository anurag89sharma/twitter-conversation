from fabric.api import local

def prepare_deployment(branch_name):
    local('python manage.py test twitter', capture=False)
    local('git add -p && git commit', capture=False)
    local('git checkout master && git merge ' + branch_name, capture=False)

def deploy():
    with lcd('/path/to/my/prod/area/'):
        local('git pull /my/path/to/dev/area/')
        local('python manage.py migrate twitter')
        local('python manage.py test twitter')
        local('/my/command/to/restart/webserver')
