"""
Concierge Controller - Flask routes for Resource Concierge chat interface.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from ...extensions import db, csrf
from .query_processor import QueryProcessor
from .response_generator import ResponseGenerator
from datetime import datetime, timedelta

concierge_bp = Blueprint('concierge', __name__, url_prefix='/concierge')

# Initialize processors
query_processor = QueryProcessor()
response_generator = ResponseGenerator()

# Cache for health check results (to avoid hitting rate limits)
_health_check_cache = {
    'result': None,
    'timestamp': None,
    'cache_duration': timedelta(seconds=180)  # Cache for 3 minutes
}


@concierge_bp.route('/query', methods=['POST'])
@csrf.exempt
@login_required
def query():
    """Process a user query and return AI response."""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        # Process query and retrieve context
        context = query_processor.process_query(
            query=user_query,
            user_role=current_user.role,
            user_id=current_user.id
        )
        
        # Generate response
        try:
            response = response_generator.generate_response(
                query=user_query,
                user_role=current_user.role,
                user_id=current_user.id,
                doc_chunks=context['doc_chunks'],
                db_results=context['db_results']
            )
        except Exception as e:
            current_app.logger.error(f"Error in response_generator.generate_response: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Error generating response: {str(e)}'
            }), 500
        
        # Log conversation (optional - can be stored in database)
        # For now, we'll just return the response
        
        # Format booking proposal if present
        booking_data = None
        if response.get('booking_proposal'):
            proposal = response['booking_proposal']
            booking_data = {
                'resource_id': proposal['resource_id'],
                'resource_title': proposal['resource_title'],
                'resource_location': proposal.get('resource_location', ''),
                'proposed_date': proposal['proposed_date'],
                'proposed_time': proposal['proposed_time'],
                'proposed_duration': proposal['proposed_duration'],
                'available': proposal.get('available', False)
            }
        
        # Log response for debugging
        current_app.logger.info(f"Concierge response generated successfully for query: {user_query[:50]}...")
        
        return jsonify({
            'success': True,
            'response': response['text'],
            'links': response.get('links', []),
            'booking_proposal': booking_data,
            'sources': response.get('sources', [])
        })
        
    except ValueError as e:
        # API key or configuration error
        current_app.logger.error(f"Concierge configuration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Concierge service is not properly configured. Please contact an administrator.'
        }), 500
    except Exception as e:
        current_app.logger.error(f"Concierge error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'An error occurred processing your query: {str(e)}. Please try again.'
        }), 500


@concierge_bp.route('/health', methods=['GET'])
def health():
    """Check if concierge service is available."""
    from .llm_client import LLMClient
    import os
    
    # Check if API key is configured (this doesn't require an API call)
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        current_app.logger.warning('OPENAI_API_KEY not found in environment')
        return jsonify({
            'available': False,
            'model': None,
            'error': 'OPENAI_API_KEY not configured. Please set it in your .env file.'
        }), 200  # Return 200 so frontend can handle it
    
    # Check cache first to avoid hitting rate limits
    now = datetime.now()
    if (_health_check_cache['result'] is not None and 
        _health_check_cache['timestamp'] is not None and
        now - _health_check_cache['timestamp'] < _health_check_cache['cache_duration']):
        # Return cached result
        cached_result = _health_check_cache['result']
        current_app.logger.debug('Returning cached health check result')
        return jsonify(cached_result)
    
    # Cache expired or doesn't exist, make actual API call
    try:
        llm_client = LLMClient()
        is_available = llm_client.is_available()
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini') if is_available else None
        
        if not is_available:
            current_app.logger.warning('OpenAI API is not available (health check failed)')
            result = {
                'available': False,
                'model': model,
                'error': 'OpenAI API is not responding. Please check your API key and internet connection.'
            }
        else:
            result = {
                'available': True,
                'model': model,
                'error': None
            }
        
        # Cache the result
        _health_check_cache['result'] = result
        _health_check_cache['timestamp'] = now
        
        return jsonify(result)
    except ValueError as e:
        # API key not configured or invalid format
        current_app.logger.error(f'LLMClient ValueError: {e}')
        result = {
            'available': False,
            'model': None,
            'error': f'Configuration error: {str(e)}'
        }
        # Cache error results for shorter duration (10 seconds)
        _health_check_cache['result'] = result
        _health_check_cache['timestamp'] = now
        _health_check_cache['cache_duration'] = timedelta(seconds=10)
        return jsonify(result), 200
    except Exception as e:
        # Other errors (network, API errors, etc.)
        current_app.logger.error(f'Concierge health check error: {e}', exc_info=True)
        error_msg = str(e)
        # Make error message more user-friendly
        if 'Authentication' in error_msg or 'Invalid' in error_msg:
            error_msg = 'Invalid API key. Please check your OPENAI_API_KEY in the .env file.'
        elif 'timeout' in error_msg.lower() or 'connection' in error_msg.lower():
            error_msg = 'Connection timeout. Please check your internet connection.'
        
        result = {
            'available': False,
            'model': None,
            'error': error_msg
        }
        # Cache error results for shorter duration (10 seconds)
        _health_check_cache['result'] = result
        _health_check_cache['timestamp'] = now
        _health_check_cache['cache_duration'] = timedelta(seconds=10)
        return jsonify(result), 200

