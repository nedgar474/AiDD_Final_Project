"""
Concierge Controller - Flask routes for Resource Concierge chat interface.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from ...extensions import db, csrf
from .query_processor import QueryProcessor
from .response_generator import ResponseGenerator

concierge_bp = Blueprint('concierge', __name__, url_prefix='/concierge')

# Initialize processors
query_processor = QueryProcessor()
response_generator = ResponseGenerator()


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
        response = response_generator.generate_response(
            query=user_query,
            user_role=current_user.role,
            user_id=current_user.id,
            doc_chunks=context['doc_chunks'],
            db_results=context['db_results']
        )
        
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
    
    try:
        llm_client = LLMClient()
        is_available = llm_client.is_available()
        model = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini') if is_available else None
    except ValueError as e:
        # API key not configured
        return jsonify({
            'available': False,
            'model': None,
            'error': 'OPENAI_API_KEY not configured'
        })
    except Exception as e:
        return jsonify({
            'available': False,
            'model': None,
            'error': str(e)
        })
    
    return jsonify({
        'available': is_available,
        'model': model
    })

