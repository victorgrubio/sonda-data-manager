from flask import Blueprint, jsonify, request
from helper import global_variables as gv
from helper import utils
from helper.cache import cache
import traceback

config = Blueprint('config', __name__, url_prefix="/videoAnalysis/config")

@config.route('/mux-programs', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
def api_get_config_mux_programs():
    try:
        mux_url = request.args.get("url")
        output_programs = gv.api_dm.config_router.get_mux_program_numbers(mux_url)
        gv.logger.info(output_programs)
        return jsonify(output_programs), 200
    except Exception as e:
        gv.logger.error(e)
        gv.logger.error(traceback.print_exc())
        return utils.build_output(task="Get programs of mux", status=500,
                                         message="Internal server error", output={}), 500
