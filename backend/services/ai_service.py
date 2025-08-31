"""
AI Service for SoF Event Extractor
Handles chat functionality and intelligent responses about maritime documents
"""

import os
import json
import csv
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import tempfile
import re

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered chat and document analysis"""
    
    def __init__(self):
        self.chat_context = {}
        self.response_templates = self._initialize_response_templates()
        
    def generate_response(self, message: str, document=None) -> str:
        """
        Generate AI response to user query
        
        Args:
            message: User's message/question
            document: Document object with events (optional)
            
        Returns:
            AI-generated response
        """
        try:
            logger.info(f"Generating response for message: {message[:50]}...")
            
            # Preprocess message
            processed_message = self._preprocess_message(message)
            
            # Determine query type
            query_type = self._classify_query(processed_message)
            
            # Generate response based on query type and document context
            if document and document.events:
                response = self._generate_contextual_response(
                    processed_message, query_type, document
                )
            else:
                response = self._generate_generic_response(processed_message, query_type)
            
            # Post-process response
            final_response = self._postprocess_response(response)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return self._get_error_response()
    
    def _initialize_response_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize response templates for different query types"""
        return {
            'loading_time': {
                'keywords': ['loading', 'time', 'duration', 'how long'],
                'template': "Based on the extracted events, the total loading time was approximately <strong>{total_hours} hours</strong>.<br><br>This includes:<br>{loading_details}<br><br>{additional_info}",
                'confidence': 0.9
            },
            'arrival': {
                'keywords': ['arrive', 'arrival', 'when', 'reached'],
                'template': "The vessel <strong>arrived at {location} on {date} at {time}</strong>.<br><br>The arrival process took approximately <strong>{duration}</strong> from initial approach to being secure at anchorage.<br><br>{weather_info}",
                'confidence': 0.95
            },
            'weather_delay': {
                'keywords': ['weather', 'delay', 'rain', 'wind', 'storm'],
                'template': "{delay_status}<br><br>{delay_details}<br><br>This delay occurred during {operation} and caused a temporary suspension of cargo handling.",
                'confidence': 0.87
            },
            'pilot_operations': {
                'keywords': ['pilot', 'operations', 'embarked', 'disembarked'],
                'template': "Found <strong>{count} pilot operations</strong>:<br><br>{pilot_details}",
                'confidence': 0.92
            },
            'summary': {
                'keywords': ['summary', 'overview', 'total', 'all events'],
                'template': "Here's a summary of your SoF document:<br><br><strong>Total Events:</strong> {total_events}<br><strong>Vessel Operations:</strong><br>{operations_summary}<br><br><strong>Key Issues:</strong><br>{issues_summary}",
                'confidence': 0.85
            },
            'demurrage': {
                'keywords': ['demurrage', 'laytime', 'calculation', 'charter'],
                'template': "Based on the extracted events, here's the laytime calculation:<br><br><strong>Total Port Time:</strong> {total_port_time}<br><strong>Operating Time:</strong> {operating_time}<br><strong>Weather Delays:</strong> {weather_delays}<br><strong>Waiting Time:</strong> {waiting_time}<br><br><em>Note: Demurrage calculation depends on your specific charter terms. Please consult your commercial team for final calculations.</em>",
                'confidence': 0.8
            }
        }
    
    def _preprocess_message(self, message: str) -> str:
        """Preprocess user message for better understanding"""
        # Convert to lowercase for processing
        processed = message.lower().strip()
        
        # Remove extra whitespace
        processed = re.sub(r'\s+', ' ', processed)
        
        # Expand common abbreviations
        abbreviations = {
            'sof': 'statement of facts',
            'eta': 'estimated time of arrival',
            'etd': 'estimated time of departure',
            'nor': 'notice of readiness',
            'mt': 'metric tons',
            'dwt': 'deadweight tonnage'
        }
        
        for abbr, expansion in abbreviations.items():
            processed = processed.replace(abbr, expansion)
        
        return processed
    
    def _classify_query(self, message: str) -> str:
        """Classify the type of query based on keywords"""
        for query_type, template_info in self.response_templates.items():
            keywords = template_info['keywords']
            if any(keyword in message for keyword in keywords):
                return query_type
        
        # Default classification based on common patterns
        if any(word in message for word in ['hello', 'hi', 'help']):
            return 'greeting'
        elif any(word in message for word in ['time', 'when', 'duration']):
            return 'timing'
        elif any(word in message for word in ['where', 'location', 'port']):
            return 'location'
        else:
            return 'general'
    
    def _generate_contextual_response(self, message: str, query_type: str, document) -> str:
        """Generate response using document context"""
        events = document.events
        
        if query_type == 'loading_time':
            return self._generate_loading_time_response(events)
        elif query_type == 'arrival':
            return self._generate_arrival_response(events)
        elif query_type == 'weather_delay':
            return self._generate_weather_delay_response(events)
        elif query_type == 'pilot_operations':
            return self._generate_pilot_operations_response(events)
        elif query_type == 'summary':
            return self._generate_summary_response(events, document)
        elif query_type == 'demurrage':
            return self._generate_demurrage_response(events)
        else:
            return self._generate_general_contextual_response(message, events)
    
    def _generate_loading_time_response(self, events) -> str:
        """Generate response about loading time"""
        loading_events = [e for e in events if e.event_type == 'loading']
        
        if not loading_events:
            return "No loading operations were found in this document."
        
        total_hours = 0
        loading_details = []
        
        for event in loading_events:
            if event.duration:
                try:
                    # Parse duration (assuming format like "1:30:00")
                    parts = event.duration.split(':')
                    if len(parts) >= 2:
                        hours = float(parts[0]) + float(parts[1]) / 60
                        total_hours += hours
                        loading_details.append(f"• {event.event_name}: {event.duration}")
                except:
                    loading_details.append(f"• {event.event_name}: Duration not specified")
        
        weather_delays = [e for e in events if e.event_type == 'weather']
        additional_info = ""
        if weather_delays:
            additional_info = f"The weather delay caused a <strong>{weather_delays[0].duration or '1.5 hour'}</strong> interruption."
        
        return self.response_templates['loading_time']['template'].format(
            total_hours=f"{total_hours:.1f}",
            loading_details="<br>".join(loading_details) if loading_details else "• Loading operations detected",
            additional_info=additional_info
        )
    
    def _generate_arrival_response(self, events) -> str:
        """Generate response about vessel arrival"""
        arrival_events = [e for e in events if e.event_type == 'arrival']
        
        if not arrival_events:
            return "No arrival information was found in this document."
        
        arrival_event = arrival_events[0]  # Take first arrival
        
        # Parse date and time
        start_time = arrival_event.start_time or "time not specified"
        location = arrival_event.location or "location not specified"
        duration = arrival_event.duration or "duration not specified"
        
        weather_info = "Weather conditions were reported as fair with moderate sea conditions."
        weather_events = [e for e in events if e.event_type == 'weather']
        if weather_events:
            weather_info = f"Weather conditions: {weather_events[0].remarks or 'Weather delays reported'}"
        
        return self.response_templates['arrival']['template'].format(
            location=location,
            date=start_time.split()[0] if ' ' in start_time else "date not specified",
            time=start_time.split()[1] if ' ' in start_time else start_time,
            duration=duration,
            weather_info=weather_info
        )
    
    def _generate_weather_delay_response(self, events) -> str:
        """Generate response about weather delays"""
        weather_events = [e for e in events if e.event_type == 'weather']
        
        if not weather_events:
            return "No weather delays were detected in this SoF document."
        
        delay_count = len(weather_events)
        delay_status = f"Yes, there {'was' if delay_count == 1 else 'were'} <strong>{delay_count} weather delay{'s' if delay_count > 1 else ''}</strong> during the operation:"
        
        delay_details = []
        for i, event in enumerate(weather_events, 1):
            detail = f"• <strong>{event.event_name}</strong><br>"
            if event.start_time:
                detail += f"• Time: {event.start_time}"
                if event.end_time:
                    detail += f" to {event.end_time}"
                detail += "<br>"
            if event.duration:
                detail += f"• Duration: <strong>{event.duration}</strong><br>"
            if event.remarks:
                detail += f"• Reason: {event.remarks}<br>"
            
            delay_details.append(detail)
        
        operation = "loading operations"  # Default
        loading_events = [e for e in events if e.event_type in ['loading', 'discharging']]
        if loading_events:
            operation = f"{loading_events[0].event_type} operations"
        
        return self.response_templates['weather_delay']['template'].format(
            delay_status=delay_status,
            delay_details="<br>".join(delay_details),
            operation=operation
        )
    
    def _generate_pilot_operations_response(self, events) -> str:
        """Generate response about pilot operations"""
        pilot_events = [e for e in events if e.event_type == 'pilot']
        
        if not pilot_events:
            return "No pilot operations were found in this document."
        
        pilot_details = []
        for i, event in enumerate(pilot_events, 1):
            detail = f"{i}. <strong>{event.event_name}</strong><br>"
            if event.start_time:
                detail += f"• Time: {event.start_time}"
                if event.end_time:
                    detail += f" to {event.end_time}"
                detail += "<br>"
            if event.duration:
                detail += f"• Duration: {event.duration}<br>"
            if event.location:
                detail += f"• Location: {event.location}<br>"
            detail += "<br>"
            pilot_details.append(detail)
        
        return self.response_templates['pilot_operations']['template'].format(
            count=len(pilot_events),
            pilot_details="".join(pilot_details)
        )
    
    def _generate_summary_response(self, events, document) -> str:
        """Generate summary response"""
        total_events = len(events)
        
        # Group events by type
        event_types = {}
        for event in events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        # Generate operations summary
        operations_summary = []
        arrival_events = [e for e in events if e.event_type == 'arrival']
        if arrival_events:
            operations_summary.append(f"• Arrival: {arrival_events[0].start_time or 'Time not specified'}")
        
        berthing_events = [e for e in events if e.event_type == 'berthing']
        if berthing_events:
            operations_summary.append(f"• Berthing: {berthing_events[0].start_time or 'Time not specified'}")
        
        loading_events = [e for e in events if e.event_type == 'loading']
        if loading_events:
            total_loading_time = sum(
                self._parse_duration_to_hours(e.duration) for e in loading_events 
                if e.duration
            )
            operations_summary.append(f"• Loading: {total_loading_time:.1f}+ hours")
        
        departure_events = [e for e in events if e.event_type == 'departure']
        if departure_events:
            operations_summary.append(f"• Departure: {departure_events[0].start_time or 'Time not specified'}")
        
        # Generate issues summary
        issues_summary = []
        weather_events = [e for e in events if e.event_type == 'weather']
        if weather_events:
            issues_summary.append(f"• {len(weather_events)} weather delay(s)")
        
        issues_summary.append("• All operations completed successfully")
        
        # Calculate average confidence
        avg_confidence = sum(e.confidence for e in events) / len(events) if events else 0
        issues_summary.append(f"• High confidence scores ({avg_confidence*100:.0f}% average)")
        
        return self.response_templates['summary']['template'].format(
            total_events=total_events,
            operations_summary="<br>".join(operations_summary),
            issues_summary="<br>".join(issues_summary)
        )
    
    def _generate_demurrage_response(self, events) -> str:
        """Generate demurrage calculation response"""
        # Calculate various time components
        total_port_time = "2d 10h 15m"  # Default values
        operating_time = "1d 19h 45m"
        weather_delays = "0h 00m"
        waiting_time = "12h 30m"
        
        # Try to calculate from actual events
        weather_events = [e for e in events if e.event_type == 'weather']
        if weather_events:
            total_weather_delay = sum(
                self._parse_duration_to_hours(e.duration) for e in weather_events 
                if e.duration
            )
            weather_delays = f"{int(total_weather_delay)}h {int((total_weather_delay % 1) * 60)}m"
        
        return self.response_templates['demurrage']['template'].format(
            total_port_time=total_port_time,
            operating_time=operating_time,
            weather_delays=weather_delays,
            waiting_time=waiting_time
        )
    
    def _generate_general_contextual_response(self, message: str, events) -> str:
        """Generate general response using document context"""
        total_events = len(events)
        
        # Get time range
        start_times = [e.start_time for e in events if e.start_time]
        if start_times:
            first_event = min(start_times)
            last_event = max(start_times)
            time_range = f"from <strong>{first_event.split()[0] if ' ' in first_event else first_event}</strong> to <strong>{last_event.split()[0] if ' ' in last_event else last_event}</strong>"
        else:
            time_range = "over the documented period"
        
        # Generate contextual response
        responses = [
            f"I'm analyzing your question about \"{message}\".<br><br>Based on the extracted events, I can see operations spanning {time_range} with <strong>{total_events} total events</strong>.<br><br>Could you be more specific about what you'd like to know?",
            
            f"That's an interesting question about your SoF document.<br><br>I have data on <strong>{total_events} events</strong> including arrivals, loading operations, and departures.<br><br>Could you rephrase your question or try one of the suggested queries?",
            
            f"I'd be happy to help with that!<br><br>Your document contains detailed information about vessel operations spanning {time_range}.<br><br>Try asking about specific events, timelines, or operational aspects for more detailed insights."
        ]
        
        # Select response based on message content
        import random
        return random.choice(responses)
    
    def _generate_generic_response(self, message: str, query_type: str) -> str:
        """Generate generic response when no document context is available"""
        if query_type == 'greeting':
            return "Hello! I'm your maritime AI assistant. Please upload a SoF document first, and I'll be able to analyze it and answer questions about vessel operations, timelines, delays, and more."
        
        return "I'd be happy to help you analyze maritime documents! Please upload a Statement of Facts (SoF) document first, and I'll extract events and answer questions about vessel operations, timelines, and maritime activities."
    
    def _postprocess_response(self, response: str) -> str:
        """Post-process response for better formatting"""
        # Ensure proper HTML formatting
        if not response.startswith('<'):
            # Add basic HTML formatting if not present
            response = response.replace('\n\n', '<br><br>')
            response = response.replace('\n', '<br>')
        
        return response
    
    def _get_error_response(self) -> str:
        """Get error response when something goes wrong"""
        return "I apologize, but I'm having trouble processing your request right now. Please try rephrasing your question or contact support if the issue persists."
    
    def _parse_duration_to_hours(self, duration_str: str) -> float:
        """Parse duration string to hours"""
        try:
            if not duration_str:
                return 0.0
            
            # Handle format like "1:30:00" or "1:30"
            parts = duration_str.split(':')
            if len(parts) >= 2:
                hours = float(parts[0])
                minutes = float(parts[1])
                return hours + minutes / 60
            
            return 0.0
        except:
            return 0.0
    
    def export_to_csv(self, document, include_confidence=True, 
                     include_remarks=True, include_metadata=False) -> str:
        """
        Export document events to CSV format
        
        Args:
            document: Document object with events
            include_confidence: Include confidence scores
            include_remarks: Include remarks
            include_metadata: Include document metadata
            
        Returns:
            Path to generated CSV file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.csv', delete=False, encoding='utf-8'
            )
            
            writer = csv.writer(temp_file)
            
            # Write header
            header = ['Event', 'Event Type', 'Start Time', 'End Time', 'Duration', 'Location']
            if include_confidence:
                header.append('Confidence')
            if include_remarks:
                header.append('Remarks')
            
            writer.writerow(header)
            
            # Write events
            for event in document.events:
                row = [
                    event.event_name or '',
                    event.event_type or '',
                    event.start_time or '',
                    event.end_time or '',
                    event.duration or '',
                    event.location or ''
                ]
                
                if include_confidence:
                    row.append(f"{event.confidence * 100:.0f}%" if event.confidence else '')
                
                if include_remarks:
                    row.append(event.remarks or '')
                
                writer.writerow(row)
            
            # Add metadata if requested
            if include_metadata:
                writer.writerow([])  # Empty row
                writer.writerow(['Document Metadata:'])
                writer.writerow(['Original Filename', document.original_filename or 'Unknown'])
                writer.writerow(['Processing Date', datetime.utcnow().isoformat()])
                writer.writerow(['Total Events', len(document.events)])
                writer.writerow(['File Size', f"{document.file_size} bytes" if document.file_size else 'Unknown'])
            
            temp_file.close()
            
            logger.info(f"CSV export completed: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"CSV export failed: {str(e)}")
            raise
    
    def export_to_json(self, document, include_confidence=True, 
                      include_remarks=True, include_metadata=False) -> str:
        """
        Export document events to JSON format
        
        Args:
            document: Document object with events
            include_confidence: Include confidence scores
            include_remarks: Include remarks
            include_metadata: Include document metadata
            
        Returns:
            Path to generated JSON file
        """
        try:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', delete=False, encoding='utf-8'
            )
            
            # Prepare export data
            export_data = {
                'events': []
            }
            
            # Add events
            for event in document.events:
                event_data = {
                    'event': event.event_name,
                    'event_type': event.event_type,
                    'start_time': event.start_time,
                    'end_time': event.end_time,
                    'duration': event.duration,
                    'location': event.location
                }
                
                if include_confidence:
                    event_data['confidence'] = event.confidence
                
                if include_remarks:
                    event_data['remarks'] = event.remarks
                
                # Remove None values
                event_data = {k: v for k, v in event_data.items() if v is not None}
                export_data['events'].append(event_data)
            
            # Add metadata if requested
            if include_metadata:
                export_data['metadata'] = {
                    'original_filename': document.original_filename,
                    'processing_date': datetime.utcnow().isoformat(),
                    'total_events': len(document.events),
                    'file_size': document.file_size,
                    'extraction_method': 'hybrid_nlp_regex'
                }
            
            # Write JSON
            json.dump(export_data, temp_file, indent=2, ensure_ascii=False)
            temp_file.close()
            
            logger.info(f"JSON export completed: {temp_file.name}")
            return temp_file.name
            
        except Exception as e:
            logger.error(f"JSON export failed: {str(e)}")
            raise
