# -*- coding: utf-8 -*-
# B2SHARE2

"""B2Share Communities REST API"""

from __future__ import absolute_import

from flask import Blueprint, jsonify

from invenio_rest import ContentNegotiatedMethodView

from .mock_impl import CommunityRegistry
from ..schemas.mock_impl import SchemaRegistry


blueprint = Blueprint(
    'b2share_communities',
    __name__,
    url_prefix='/communities'
)


def community_to_json_serializer(data, code=200, headers=None):
    """Build a json flask response using the given data.
    :Returns: A flask response with json data.
    :Returns Type: :py:class:`flask.Response`
    """
    response = jsonify(data)
    response.status_code = code
    if headers is not None:
        response.headers.extend(headers)
    # TODO: set location to seld
    # response.headers['location'] = ...
    # TODO: set etag
    # response.set_etag(...)
    return response


class CommunityListResource(ContentNegotiatedMethodView):

    view_name = 'community_list'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(CommunityListResource, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, **kwargs):
        """
        Retrieve list of communities.
        """
        return {'communities': CommunityRegistry.get_all()}

    def post(self, **kwargs):
        """
        Creates a new community that has associated a new metadata fieldset.
        Only administrators can use it.
        parameter: name, description, logo
        """
        return CommunityRegistry.create_community(kwargs)


class CommunityResource(ContentNegotiatedMethodView):

    view_name = 'community_item'

    def __init__(self, *args, **kwargs):
        """Constructor."""
        super(CommunityResource, self).__init__(*args, **kwargs)
        self.serializers = {
            'application/json': community_to_json_serializer,
        }

    def get(self, community_id, **kwargs):
        """
        Get a community metadata and description.
        """

        community = CommunityRegistry.get_by_id(community_id)
        if not community:
            community = CommunityRegistry.get_by_name(community_id)
        if not community:
            return {'message': 'Not Found', 'status': 404}, 404

        comm = {k: community[k] for k in ['id', 'name', 'domain', 'description', 'logo']}
        comm['schema_id_list'] = [{'id': sid} for sid in community['schema_id_list']]
        for sdict in comm['schema_id_list']:
            schema = SchemaRegistry.get_by_id(sdict['id'])
            sdict['link'] = schema.get('id') if schema else None
        return comm

    def patch(self, community_id, **kwargs):
        """
        Modify a community
        """
        return CommunityRegistry.get_by_id(community_id).patch_description(kwargs)


blueprint.add_url_rule('/',
                       view_func=CommunityListResource
                       .as_view(CommunityListResource.view_name))
blueprint.add_url_rule('/<path:community_id>',
                       view_func=CommunityResource
                       .as_view(CommunityResource.view_name))