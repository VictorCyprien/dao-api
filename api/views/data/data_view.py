from flask import jsonify
from flask.views import MethodView

from datetime import datetime, timedelta

from .data_blp import data_blp

from ...schemas.data_schemas import QueryParamsSchema, ItemsResponseSchema, SummaryResponseSchema
from ...schemas.communs_schemas import PagingError

from helpers.sqlite_file import get_db, query_db
from helpers.logging_file import Logger
from helpers.errors_file import BadRequest


from rich import print


logger = Logger()


@data_blp.route('/items')
class ItemsDataView(MethodView):
    @data_blp.doc(operationId='GetData')
    @data_blp.arguments(QueryParamsSchema, location="query")
    @data_blp.response(400, schema=PagingError, description="BadRequest")
    @data_blp.response(200, schema=ItemsResponseSchema, description="OK")
    def get(self, input_data: dict):
        """Get data"""
        #Expected format: YYYY-MM-DDThh:mm:ss
        date_start = input_data.get('date_start')
        date_end = input_data.get('date_end')
        source = input_data.get('source', None)

        query = ""
        timestamp_date_start = int(datetime.strptime(date_start, "%Y-%m-%d").timestamp())
        timestamp_date_end = int(datetime.strptime(date_end, "%Y-%m-%d").timestamp())
        query = f"SELECT * FROM items WHERE date >= {timestamp_date_start} AND date < {timestamp_date_end + (24 * 60 * 60)}"
        if source is not None:
            query += f" AND source = '{source}'"    

        data = query_db(query)
        # Convert list of tuples to list of dicts
        data = [dict(zip(['id', 'cid', 'type', 'source', 'title', 'text', 'link', 'topics', 'date', 'metadata'], row)) for row in data]

        # Convert source field from string to dict if it looks like a dict
        for item in data:
            source = item['source']
            if isinstance(source, str) and source.startswith('{') or source.startswith('[') and source.endswith('}') or source.endswith(']'):
                try:
                    import ast
                    item['source'] = ast.literal_eval(source)
                except:
                    # Keep as string if conversion fails
                    pass
        
        return {
            "data": data
        }
    


@data_blp.route('/summary')
class SummaryDataView(MethodView):
    @data_blp.doc(operationId='GetData')
    @data_blp.arguments(QueryParamsSchema, location="query")
    @data_blp.response(400, schema=PagingError, description="BadRequest")
    @data_blp.response(200, schema=SummaryResponseSchema, description="OK")
    def get(self, input_data: dict):
        """Get data"""
        #Expected format: YYYY-MM-DDThh:mm:ss
        date_start = input_data.get('date_start')
        date_end = input_data.get('date_end')
        source = input_data.get('source', None)
        
        start_date = datetime.strptime(date_start, "%Y-%m-%d")
        end_date = datetime.strptime(date_end, "%Y-%m-%d")
        nb_days = (end_date - start_date).days
        data = []
        for i in range(nb_days):
            current_date = start_date + timedelta(days=i)
            query = f"SELECT * FROM summary WHERE title LIKE '%Daily Summary for {current_date.strftime('%Y-%m-%d')}%'"
            query_data = query_db(query)
            data.append({
                f"{current_date.strftime('%Y-%m-%d')}": [dict(zip(['id', 'cid', 'type', 'source', 'title', 'text', 'link', 'topics', 'date', 'metadata'], row)) for row in query_data]
            })

        # Convert source field from string to dict if it looks like a dict
        for item in data:
            for summaries in item.values():
                for summary in summaries:
                    source = summary['source']
                    if isinstance(source, str) and (source.startswith('{') or source.startswith('[')) and (source.endswith('}') or source.endswith(']')):
                        try:
                            import ast
                            summary['source'] = ast.literal_eval(source)
                        except:
                            pass

        return {
            "summary": data
        }
        