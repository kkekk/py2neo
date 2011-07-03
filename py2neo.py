#!/usr/bin/env python

import httplib2
import json


class Resource:

	_GET_headers = {
		"Accept": "application/json"
	}
	_POST_headers = {
		"Accept": "application/json",
		"Content-Type": "application/json"
	}

	def __init__(self, uri):
		self._http = httplib2.Http()
		self.uri = uri
		self.index = self._get(self.uri)

	def _get(self, uri):
		response, content = self._http.request(uri, "GET", None, self._GET_headers)
		if response.status == 200:
			return json.loads(content)
		elif response.status == 204:
			return None
		elif response.status == 404:
			raise KeyError(uri)
		else:
			raise SystemError("%s %s" % (response.status, response.reason))

	def _post(self, uri, data):
		data = {} if data == None else json.dumps(data)
		response, content = self._http.request(uri, "POST", data, self._POST_headers)
		if response.status == 201:
			return response["location"]
		elif response.status == 400:
			raise ValueError(data)
		else:
			raise SystemError("%s %s" % (response.status, response.reason))

	def _put(self, uri, data):
		data = {} if data == None else json.dumps(data)
		response, content = self._http.request(uri, "PUT", data, self._POST_headers)
		if response.status == 204:
			pass
		elif response.status == 400:
			raise ValueError(data)
		elif response.status == 404:
			raise KeyError(uri)
		else:
			raise SystemError("%s %s" % (response.status, response.reason))

	def _delete(self, uri):
		response, content = self._http.request(uri, "DELETE", None, self._GET_headers)
		if response.status == 204:
			pass
		elif response.status == 404:
			raise KeyError(uri)
		else:
			raise SystemError("%s %s" % (response.status, response.reason))

	def __repr__(self):
		return self.uri


class GraphDatabaseService(Resource):

	def __init__(self, uri):
		Resource.__init__(self, uri)

	def create_node(self, properties=None):
		return Node(self._post(self.index["node"], properties))

	def get_relationship_types(self):
		return self._get(self.index["relationship_types"])


class Node(Resource):

	def __init__(self, uri):
		Resource.__init__(self, uri)

	def set_properties(self, properties):
		self._put(self.index["properties"], properties)

	def get_properties(self):
		return self._get(self.index["properties"])

	def remove_properties(self):
		self._delete(self.index["properties"])

	def __setitem__(self, key, value):
		self._put(self.index["property"].format(key=key), value)

	def __getitem__(self, key):
		return self._get(self.index["property"].format(key=key))

	def __delitem__(self, key):
		self._delete(self.index["property"].format(key=key))

	def delete(self):
		self._delete(self.index["self"])

	def create_relationship(self, to, data, type):
		return Relationship(self._post(self.index["create_relationship"], {
			"to": str(to),
			"data": data,
			"type": type
		}))

	def get_all_relationships(self, *types):
		if len(types) == 0:
			uri = self.index["all_relationships"]
		else:
			uri = self.index["all_typed_relationships"].replace("{-list|&|types}", "&".join(types))
		return self._get(uri)

	def get_incoming_relationships(self, *types):
		if len(types) == 0:
			uri = self.index["incoming_relationships"]
		else:
			uri = self.index["incoming_typed_relationships"].replace("{-list|&|types}", "&".join(types))
		return self._get(uri)

	def get_outgoing_relationships(self, *types):
		if len(types) == 0:
			uri = self.index["outgoing_relationships"]
		else:
			uri = self.index["outgoing_typed_relationships"].replace("{-list|&|types}", "&".join(types))
		return self._get(uri)


class Relationship(Resource):

	def __init__(self, uri):
		Resource.__init__(self, uri)

	def set_properties(self, properties):
		self._put(self.index["properties"], properties)

	def get_properties(self):
		return self._get(self.index["properties"])

	def remove_properties(self):
		self._delete(self.index["properties"])

	def __setitem__(self, key, value):
		self._put(self.index["property"].format(key=key), value)

	def __getitem__(self, key):
		return self._get(self.index["property"].format(key=key))

	def __delitem__(self, key):
		self._delete(self.index["property"].format(key=key))

	def delete(self):
		self._delete(self.index["self"])


