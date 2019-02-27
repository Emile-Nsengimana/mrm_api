null = None

update_room_resource_query = '''
            mutation{
            updateRoomResource(resourceId:1,name:"Markers",roomId:1){
                resource{
                name
                }
            }
            }
            '''

expected_update_room_resource_query = {
    "data": {
        "updateRoomResource": {
            "resource": {
                "name": "Markers"
            }
        }
    }
}


non_existant_resource_id_query = '''
                        mutation{
                        updateRoomResource(resourceId:6,name:"TV Screen"){
                            resource{
                            name
                            }
                        }
                        }
                        '''

expected_non_existant_resource_id_query = {
    "errors": [
        {
            "message": "ResourceId not Found",
            "locations": [
                {
                    "line": 3,
                    "column": 25
                }
            ]
        }
    ],
    "data": {
        "updateRoomResource": null
    }
}

update_with_empty_field = '''
                    mutation{
                        updateRoomResource(resourceId:1,name:""){
                            resource{
                            name
                            }
                        }
                        }
'''

expected_response_empty_field = {
    "errors": [
        {
            "message": "name is required field",
            "locations": [
                {
                    "line": 3,
                    "column": 25
                }
            ]
        }
    ],
    "data": {
        "updateRoomResource": null
    }

}

response_for_update_room_resource_with_database_error = {
    "errors": [
        {
            "message": "There seems to be a database connection error, contact your administrator for assistance",  # noqa
            "locations": [
                {

                    "line": 3,
                    "column": 13
                }
                ],
            "path": [
                "updateRoomResource"
            ]
        }
    ],
    "data": {"updateRoomResource": null}}
