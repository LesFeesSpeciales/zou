from flask import request, abort
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required

from zou.app.services import (
    breakdown_service,
    shots_service,
    tasks_service,
    projects_service,
    user_service
)
from zou.app.utils import query, permissions

from zou.app.services.exception import ShotNotFoundException


class ArgsMixin(object):
    def get_args(self, descriptors):
        parser = reqparse.RequestParser()
        for (name, default, required) in descriptors:
            if required is None:
                required = False
            parser.add_argument(name, required=required, default=default)

        return parser.parse_args()


class ShotResource(Resource):

    @jwt_required
    def get(self, shot_id):
        """
        Retrieve given shot.
        """
        shot = shots_service.get_full_shot(shot_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(shot["project_id"])
        return shot

    @jwt_required
    def delete(self, shot_id):
        try:
            permissions.check_manager_permissions()
            deleted_shot = shots_service.remove_shot(shot_id)
        except ShotNotFoundException:
            abort(404)
        except permissions.PermissionDenied:
            abort(403)

        return deleted_shot, 204


class SceneResource(Resource):

    @jwt_required
    def get(self, scene_id):
        """
        Retrieve given scene.
        """
        scene = shots_service.get_full_scene(scene_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(scene["project_id"])

        return scene

    @jwt_required
    def delete(self, scene_id):
        permissions.check_manager_permissions()
        deleted_scene = shots_service.remove_scene(scene_id)

        return deleted_scene, 204


class ShotsResource(Resource):

    @jwt_required
    def get(self):
        """
        Retrieve all shot entries. Filters can be specified in the query string.
        """
        criterions = query.get_query_criterions_from_request(request)
        if not permissions.has_manager_permissions():
            user_service.check_criterions_has_task_related(criterions)
        return shots_service.get_shots(criterions)


class ScenesResource(Resource):

    @jwt_required
    def get(self):
        """
        Retrieve all scene entries. Filters can be specified in the query
        string.
        """
        criterions = query.get_query_criterions_from_request(request)
        if not permissions.has_manager_permissions():
            user_service.check_criterions_has_task_related(criterions)
        return shots_service.get_scenes(criterions)


class ShotAssetsResource(Resource):

    @jwt_required
    def get(self, shot_id):
        """
        Retrieve all assets for a given shot.
        """
        shot = shots_service.get_shot(shot_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(shot["project_id"])
        return shots_service.get_entities_out(shot_id)


class ShotTaskTypesResource(Resource):

    @jwt_required
    def get(self, shot_id):
        """
        Retrieve all task types related to a given shot.
        """
        shot = shots_service.get_shot(shot_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(shot["project_id"])
        return tasks_service.get_task_types_for_shot(shot_id)


class ShotTasksResource(Resource):

    @jwt_required
    def get(self, shot_id):
        """
        Retrieve all tasks related to a given shot.
        """
        shot = shots_service.get_shot(shot_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(shot["project_id"])
        return tasks_service.get_tasks_for_shot(shot_id)


class SequenceTasksResource(Resource):

    @jwt_required
    def get(self, sequence_id):
        """
        Retrieve all tasks related to a given shot.
        """
        sequence = shots_service.get_sequence(sequence_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(sequence["project_id"])
        return tasks_service.get_tasks_for_sequence(sequence_id)


class SequenceTaskTypesResource(Resource):

    @jwt_required
    def get(self, sequence_id):
        """
        Retrieve all task types related to a given shot.
        """
        sequence = shots_service.get_sequence(sequence_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(sequence["project_id"])
        return tasks_service.get_task_types_for_sequence(sequence_id)


class ShotsAndTasksResource(Resource):

    @jwt_required
    def get(self):
        """
        Retrieve all shots, adds project name and asset type name and all
        related tasks.
        """
        criterions = query.get_query_criterions_from_request(request)
        if not permissions.has_manager_permissions():
            user_service.check_criterions_has_task_related(criterions)
        return shots_service.get_shots_and_tasks(criterions)


class ProjectShotsResource(Resource):

    @jwt_required
    def get(self, project_id):
        """
        Retrieve all shots related to a given project.
        """
        projects_service.get_project(project_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(project_id)
        return shots_service.get_shots_for_project(project_id)

    @jwt_required
    def post(self, project_id):
        """
        Create a shot for given project.
        """
        (sequence_id, name, data) = self.get_arguments()
        projects_service.get_project(project_id)
        permissions.check_manager_permissions()
        shot = shots_service.create_shot(
            project_id,
            sequence_id,
            name,
            data=data
        )
        return shot, 201

    def get_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        parser.add_argument("sequence_id", default=None)
        parser.add_argument("data", type=dict)
        args = parser.parse_args()
        return (args["sequence_id"], args["name"], args["data"])


class ProjectSequencesResource(Resource):

    @jwt_required
    def get(self, project_id):
        """
        Retrieve all sequences related to a given project.
        """
        projects_service.get_project(project_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(project_id)
        return shots_service.get_sequences_for_project(project_id)

    @jwt_required
    def post(self, project_id):
        """
        Create a sequence for given project.
        """
        (episode_id, name) = self.get_arguments()
        projects_service.get_project(project_id)
        permissions.check_manager_permissions()
        sequence = shots_service.create_sequence(
            project_id,
            episode_id,
            name
        )
        return sequence, 201

    def get_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        parser.add_argument("episode_id", default=None)
        args = parser.parse_args()
        return (args["episode_id"], args["name"])


class ProjectEpisodesResource(Resource):

    @jwt_required
    def get(self, project_id):
        """
        Retrieve all episodes related to a given project.
        """
        projects_service.get_project(project_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(project_id)
        return shots_service.get_episodes_for_project(project_id)

    @jwt_required
    def post(self, project_id):
        """
        Create an episode for given project.
        """
        name = self.get_arguments()
        projects_service.get_project(project_id)
        permissions.check_manager_permissions()
        return shots_service.create_episode(project_id, name), 201

    def get_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        args = parser.parse_args()
        return args["name"]


class EpisodeResource(Resource):

    @jwt_required
    def get(self, episode_id):
        """
        Retrieve given episode.
        """
        episode = shots_service.get_full_episode(episode_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(episode["project_id"])
        return episode


class EpisodesResource(Resource):

    @jwt_required
    def get(self):
        """
        Retrieve all episode entries. Filters can be specified in the query
        string.
        """
        criterions = query.get_query_criterions_from_request(request)
        if not permissions.has_manager_permissions():
            user_service.check_criterions_has_task_related(criterions)
        return shots_service.get_episodes(criterions)


class EpisodeSequencesResource(Resource):

    @jwt_required
    def get(self, episode_id):
        """
        Retrieve all sequence entries for a given episode.
        Filters can be specified in the query string.
        """
        episode = shots_service.get_episode(episode_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(episode["project_id"])

        criterions = query.get_query_criterions_from_request(request)
        criterions["parent_id"] = episode_id
        return shots_service.get_sequences(criterions)


class SequenceResource(Resource):

    @jwt_required
    def get(self, sequence_id):
        """
        Retrieve given sequence.
        """
        sequence = shots_service.get_full_sequence(sequence_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(sequence["project_id"])
        return sequence


class SequencesResource(Resource):

    @jwt_required
    def get(self):
        """
        Retrieve all sequence entries. Filters can be specified in the query
        string.
        """
        criterions = query.get_query_criterions_from_request(request)
        if not permissions.has_manager_permissions():
            user_service.check_criterions_has_task_related(criterions)
        return shots_service.get_sequences(criterions)


class SequenceShotsResource(Resource):

    @jwt_required
    def get(self, sequence_id):
        """
        Retrieve all shot entries for a given sequence.
        Filters can be specified in the query string.
        """
        sequence = shots_service.get_sequence(sequence_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(sequence["project_id"])
        criterions = query.get_query_criterions_from_request(request)
        criterions["parent_id"] = sequence_id
        return shots_service.get_shots(criterions)


class CastingResource(Resource):

    @jwt_required
    def get(self, shot_id):
        """
        Resource to retrieve the casting of a given shot.
        """
        shot = shots_service.get_shot(shot_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(shot["project_id"])
        return breakdown_service.get_casting(shot_id)

    @jwt_required
    def put(self, shot_id):
        """
        Resource to allow the modification of assets linked to a shot.
        """
        casting = request.json
        permissions.check_manager_permissions()
        return breakdown_service.update_casting(shot_id, casting)


class ProjectScenesResource(Resource):

    @jwt_required
    def get(self, project_id):
        """
        Retrieve all shots related to a given project.
        """
        projects_service.get_project(project_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(project_id)
        return shots_service.get_scenes_for_project(project_id)

    @jwt_required
    def post(self, project_id):
        """
        Create a shot for given project.
        """
        (sequence_id, name) = self.get_arguments()
        projects_service.get_project(project_id)
        permissions.check_manager_permissions()
        scene = shots_service.create_scene(
            project_id,
            sequence_id,
            name
        )
        return scene, 201

    def get_arguments(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", required=True)
        parser.add_argument("sequence_id", default=None)
        args = parser.parse_args()
        return (args["sequence_id"], args["name"])


class SequenceScenesResource(Resource):

    @jwt_required
    def get(self, sequence_id):
        """
        Retrieve all scenes related to a given sequence.
        """
        sequence = shots_service.get_sequence(sequence_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(sequence["project_id"])
        return shots_service.get_scenes_for_sequence(sequence_id)


class SceneTaskTypesResource(Resource):

    @jwt_required
    def get(self, scene_id):
        """
        Retrieve all task types related to a given scene.
        """
        scene = shots_service.get_scene(scene_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(scene["project_id"])
        return tasks_service.get_task_types_for_scene(scene_id)


class SceneTasksResource(Resource):

    @jwt_required
    def get(self, scene_id):
        """
        Retrieve all tasks related to a given scene.
        """
        scene = shots_service.get_scene(scene_id)
        if not permissions.has_manager_permissions():
            user_service.check_has_task_related(scene["project_id"])
        return tasks_service.get_tasks_for_scene(scene_id)


class ShotAssetInstancesResource(Resource, ArgsMixin):

    @jwt_required
    def get(self, shot_id):
        """
        Retrieve all asset instances linked to shot.
        """
        shot = shots_service.get_shot(shot_id)
        user_service.check_project_access(shot["project_id"])
        return breakdown_service.get_asset_instances_for_shot(shot_id)

    @jwt_required
    def post(self, shot_id):
        """
        Create an asset instance on given shot.
        """
        args = self.get_args([
            ("asset_id", None, True),
            ("description", None, False)
        ])
        shot = shots_service.get_shot(shot_id)
        permissions.check_manager_permissions()
        shot = breakdown_service.add_asset_instance_to_shot(
            shot_id,
            args["asset_id"],
            args["description"]
        )
        return shot, 201
