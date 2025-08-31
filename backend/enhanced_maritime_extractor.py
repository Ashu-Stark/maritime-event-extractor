#!/usr/bin/env python3
"""
Enhanced Maritime Event Extractor
Advanced NLP-based event extraction with comprehensive maritime keyword patterns
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime
import spacy
from collections import defaultdict

logger = logging.getLogger(__name__)


class EnhancedMaritimeExtractor:
    """Enhanced maritime event extractor with comprehensive patterns and NLP"""
    
    def __init__(self):
        # Load spaCy model for NLP processing
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ Loaded spaCy model for NLP processing")
        except OSError:
            logger.warning("⚠️ spaCy model not available, using fallback patterns")
            self.nlp = None
        
        # Comprehensive maritime event patterns
        self.event_patterns = self._initialize_patterns()
        
        # Maritime keywords and entities
        self.maritime_keywords = self._initialize_keywords()
        
        # Confidence scoring weights
        self.confidence_weights = {
            'exact_match': 0.95,
            'partial_match': 0.85,
            'context_match': 0.75,
            'keyword_match': 0.65
        }
    
    def _initialize_patterns(self) -> List[Dict[str, Any]]:
        """Initialize comprehensive maritime event patterns"""
        return [
            # ARRIVAL EVENTS
            {
                'type': 'arrival',
                'name': 'Vessel Arrived at Port',
                'patterns': [
                    r'(?i)vessel\s+arrived\s+(?:at\s+)?([A-Za-z\s]+?)'
                    r'(?:\s+port\s+limits?)?\s*[:=]\s*(\d{4})\s*hrs?\s*'
                    r'(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)vessel\s+arrived\s*[:=]\s*(\d{4})\s*hrs?\s*'
                    r'(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)arrived\s+(?:at\s+)?([A-Za-z\s]+?)'
                    r'(?:\s+port\s+limits?)?\s*[:=]\s*(\d{4})\s*hrs?\s*'
                    r'(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)arrived\s*[:=]\s*(\d{4})\s*hrs?\s*'
                    r'(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['arrived', 'arrival', 'reached', 'entered port'],
                'confidence': 0.95
            },
            {
                'type': 'arrival',
                'name': 'Vessel Dropped Anchor',
                'patterns': [
                    r'(?i)(?:vessel\s+)?dropped\s+anchor\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)(?:vessel\s+)?dropped\s+anchor\s+(?:at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)anchored\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['dropped anchor', 'anchored', 'anchor dropped'],
                'confidence': 0.95
            },
            {
                'type': 'arrival',
                'name': 'Vessel at Anchorage',
                'patterns': [
                    r'(?i)vessel\s+(?:at\s+)?anchorage\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)at\s+anchorage\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['at anchorage', 'anchorage', 'anchored'],
                'confidence': 0.90
            },
            
            # PILOT EVENTS
            {
                'type': 'pilot',
                'name': 'Pilot Boarded',
                'patterns': [
                    r'(?i)pilot\s+(?:boarded|embarked)(?:\s+the\s+vessel\s+for\s+berthing)?\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)pilot\s+(?:boarded|embarked)(?:\s+at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)pilot\s+(?:boarded|embarked)',
                ],
                'keywords': ['pilot boarded', 'pilot embarked', 'pilot on board'],
                'confidence': 0.95
            },
            {
                'type': 'pilot',
                'name': 'Pilot Disembarked',
                'patterns': [
                    r'(?i)pilot\s+disembarked\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)pilot\s+disembarked\s+(?:at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)pilot\s+disembarked',
                ],
                'keywords': ['pilot disembarked', 'pilot left', 'pilot off'],
                'confidence': 0.95
            },
            
            # BERTHING EVENTS
            {
                'type': 'berthing',
                'name': 'First Line Ashore',
                'patterns': [
                    r'(?i)first\s+line\s+ashore\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)first\s+line\s+ashore\s+(?:berth\s+no\s+)?([A-Z0-9\-]+)\s+(?:at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['first line ashore', 'first line', 'line ashore'],
                'confidence': 0.95
            },
            {
                'type': 'berthing',
                'name': 'All Fast Alongside',
                'patterns': [
                    r'(?i)all\s+fast\s+(?:at\s+berth\s*[-]?[A-Z0-9]+)?\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)all\s+fast\s+(?:at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)all\s+fast',
                ],
                'keywords': ['all fast', 'fast alongside', 'securely moored'],
                'confidence': 0.95
            },
            {
                'type': 'berthing',
                'name': 'Vessel Berthed',
                'patterns': [
                    r'(?i)vessel\s+berthed\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)berthed\s+(?:at\s+)?([A-Za-z\s]+?)(?:\s+terminal)?\s+(?:at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['berthed', 'berthing', 'moored', 'alongside'],
                'confidence': 0.90
            },
            
            # CARGO OPERATIONS
            {
                'type': 'cargo',
                'name': 'Loading Commenced',
                'patterns': [
                    r'(?i)loading\s+commenced(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})(?:\s+at\s+)?(\d{1,2}:\d{2})',
                    r'(?i)loading\s+commenced(?:\s+at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)loading\s+commenced\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)loading\s+commenced',
                ],
                'keywords': ['loading commenced', 'loading started', 'cargo loading'],
                'confidence': 0.95
            },
            {
                'type': 'cargo',
                'name': 'Loading Completed',
                'patterns': [
                    r'(?i)loading\s+completed(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})(?:\s+at\s+)?(\d{1,2}:\d{2})',
                    r'(?i)loading\s+completed(?:\s+at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)loading\s+completed\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)loading\s+completed',
                ],
                'keywords': ['loading completed', 'loading finished', 'cargo loaded'],
                'confidence': 0.95
            },
            {
                'type': 'cargo',
                'name': 'Discharging Commenced',
                'patterns': [
                    r'(?i)commenced\s+discharging\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)discharging\s+commenced(?:\s+at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)discharging\s+commenced',
                ],
                'keywords': ['discharging commenced', 'discharge started', 'unloading'],
                'confidence': 0.95
            },
            {
                'type': 'cargo',
                'name': 'Discharging Completed',
                'patterns': [
                    r'(?i)discharging\s+completed\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)discharging\s+completed(?:\s+at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)discharging\s+completed',
                ],
                'keywords': ['discharging completed', 'discharge finished', 'unloading complete'],
                'confidence': 0.95
            },
            
            # DEPARTURE EVENTS
            {
                'type': 'departure',
                'name': 'Vessel Departed',
                'patterns': [
                    r'(?i)(?:vessel\s+)?departed(?:\s+from\s+)?([A-Za-z\s]+?)(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})(?:\s+at\s+)?(\d{1,2}:\d{2})',
                    r'(?i)(?:vessel\s+)?departed(?:\s+at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)(?:vessel\s+)?departed\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)(?:vessel\s+)?departed',
                ],
                'keywords': ['departed', 'sailed', 'left port', 'cast off'],
                'confidence': 0.95
            },
            {
                'type': 'departure',
                'name': 'Vessel Sailed',
                'patterns': [
                    r'(?i)vessel\s+sailed\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)sailed\s+(?:at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['sailed', 'sailing', 'departed'],
                'confidence': 0.90
            },
            
            # CUSTOMS EVENTS
            {
                'type': 'customs',
                'name': 'Customs Boarding',
                'patterns': [
                    r'(?i)customs\s+boarding\s+formalities\s+commenced\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)customs\s+onboard\s+(?:at\s+)?(\d{1,2}:\d{2})(?:\s+on\s+)?(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)customs\s+boarding',
                ],
                'keywords': ['customs boarding', 'customs onboard', 'customs formalities'],
                'confidence': 0.90
            },
            
            # WEATHER EVENTS
            {
                'type': 'weather',
                'name': 'Weather Delay',
                'patterns': [
                    r'(?i)(?:heavy\s+)?(?:rain|storm|fog|wind)(?:\s+caused\s+delay)?',
                    r'(?i)weather\s+delay',
                    r'(?i)operations?\s+suspended\s+due\s+to\s+weather',
                    r'(?i)rain\s+stopped\s+work',
                ],
                'keywords': ['weather delay', 'rain delay', 'storm delay', 'fog delay'],
                'confidence': 0.90
            },
            
            # NOTICE OF READINESS
            {
                'type': 'nor',
                'name': 'NOR Tendered',
                'patterns': [
                    r'(?i)nor\s+tendered\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)notice\s+of\s+readiness\s+tendered\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['nor tendered', 'notice of readiness', 'nor'],
                'confidence': 0.95
            },
            {
                'type': 'nor',
                'name': 'NOR Accepted',
                'patterns': [
                    r'(?i)nor\s+accepted\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)notice\s+of\s+readiness\s+accepted\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['nor accepted', 'nor accepted by', 'readiness accepted'],
                'confidence': 0.95
            },
            
            # FREE PRATIQUE
            {
                'type': 'pratique',
                'name': 'Free Pratique Granted',
                'patterns': [
                    r'(?i)free\s+pratique\s+granted\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                    r'(?i)pratique\s+granted\s*[:=]\s*(\d{4})\s*hrs?\s*(\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4})',
                ],
                'keywords': ['free pratique', 'pratique granted', 'pratique'],
                'confidence': 0.95
            }
        ]
    
    def _initialize_keywords(self) -> Dict[str, List[str]]:
        """Initialize comprehensive maritime keywords"""
        return {
            'vessel_indicators': [
                'vessel', 'mv', 'm/v', 'ship', 'm.v.', 'm/vessel', 'vessel name',
                'vessel name / voy', 'name of the vessel', 'vessel / voy'
            ],
            'port_indicators': [
                'port', 'terminal', 'berth', 'quay', 'wharf', 'dock', 'harbor', 'harbour',
                'port of loading', 'port of discharge', 'port of call', 'port limits'
            ],
            'time_indicators': [
                'hrs', 'hours', 'time', 'at', 'on', 'commenced', 'completed', 'started', 'finished'
            ],
            'date_indicators': [
                'date', 'day', 'on', 'at', 'from', 'to', 'period'
            ],
            'cargo_indicators': [
                'cargo', 'loading', 'discharging', 'unloading', 'mt', 'tonnes', 'tons',
                'bulk', 'container', 'general cargo', 'cargo description'
            ],
            'operation_indicators': [
                'commenced', 'completed', 'started', 'finished', 'suspended', 'resumed',
                'stopped', 'delayed', 'interrupted'
            ]
        }
    
    def extract_events(self, text: str) -> List[Dict[str, Any]]:
        """Extract events from text using enhanced pattern matching and NLP"""
        if not text or len(text.strip()) < 10:
            logger.warning("Text too short for meaningful event extraction")
            return []
        
        events = []
        logger.info(f"Extracting events from {len(text)} characters")
        
        # Extract events using all patterns
        for pattern_info in self.event_patterns:
            events.extend(self._extract_with_patterns(text, pattern_info))
        
        # Use NLP for additional context-based extraction
        if self.nlp:
            nlp_events = self._extract_with_nlp(text)
            events.extend(nlp_events)
        
        # Remove duplicates and sort by time
        events = self._remove_duplicates(events)
        events = self._sort_events_by_time(events)
        
        # Enhance events with additional context
        events = self._enhance_events_with_context(events, text)
        
        logger.info(f"Total events extracted: {len(events)}")
        return events
    
    def _extract_with_patterns(self, text: str, pattern_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract events using multiple patterns for a single event type"""
        events = []
        
        for pattern in pattern_info['patterns']:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                event_data = self._extract_structured_event(match, pattern_info, text)
                if event_data:
                    events.append(event_data)
                    logger.info(f"Found event: {event_data['event']} ({event_data['event_type']}) at {event_data['start_time']}")
        
        return events
    
    def _extract_with_nlp(self, text: str) -> List[Dict[str, Any]]:
        """Extract events using NLP analysis"""
        events = []
        
        try:
            doc = self.nlp(text)
            
            # Extract time entities
            time_entities = [ent.text for ent in doc.ents if ent.label_ in ['TIME', 'DATE']]
            
            # Extract vessel and port mentions
            vessel_mentions = []
            port_mentions = []
            
            for sent in doc.sents:
                sent_text = sent.text.lower()
                
                # Check for vessel indicators
                if any(keyword in sent_text for keyword in self.maritime_keywords['vessel_indicators']):
                    vessel_mentions.append(sent.text)
                
                # Check for port indicators
                if any(keyword in sent_text for keyword in self.maritime_keywords['port_indicators']):
                    port_mentions.append(sent.text)
                
                # Check for operation indicators
                if any(keyword in sent_text for keyword in self.maritime_keywords['operation_indicators']):
                    # Try to identify event type from context
                    event_type = self._identify_event_type_from_context(sent_text)
                    if event_type:
                        events.append({
                            'event_type': event_type,
                            'event': f"NLP Detected {event_type.title()}",
                            'confidence': 0.70,
                            'start_time': None,
                            'location': None,
                            'remarks': sent.text,
                            'extraction_method': 'nlp_context'
                        })
            
        except Exception as e:
            logger.warning(f"NLP extraction failed: {e}")
        
        return events
    
    def _identify_event_type_from_context(self, text: str) -> str:
        """Identify event type from text context"""
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in ['arrived', 'arrival', 'reached']):
            return 'arrival'
        elif any(keyword in text_lower for keyword in ['departed', 'sailed', 'left']):
            return 'departure'
        elif any(keyword in text_lower for keyword in ['berthed', 'moored', 'alongside']):
            return 'berthing'
        elif any(keyword in text_lower for keyword in ['loading', 'loaded']):
            return 'cargo'
        elif any(keyword in text_lower for keyword in ['discharging', 'discharged', 'unloading']):
            return 'cargo'
        elif any(keyword in text_lower for keyword in ['pilot', 'boarded', 'embarked']):
            return 'pilot'
        elif any(keyword in text_lower for keyword in ['customs', 'boarding']):
            return 'customs'
        elif any(keyword in text_lower for keyword in ['weather', 'rain', 'storm', 'delay']):
            return 'weather'
        
        return None
    
    def _extract_structured_event(self, match, pattern_info: Dict[str, Any], text: str) -> Dict[str, Any]:
        """Extract structured event data from regex match"""
        try:
            full_match = match.group(0)
            groups = match.groups()
            
            # Extract time and date information
            time_info = None
            date_info = None
            location_info = None
            
            if len(groups) >= 2:
                # Try to identify time and date from groups
                for group in groups:
                    if group:
                        # Check if it's a time (HH:MM or HHMM)
                        if re.match(r'^\d{1,2}:\d{2}$', group) or re.match(r'^\d{4}$', group):
                            time_info = group
                        # Check if it's a date (DD/MM/YYYY, DD.MM.YYYY, etc.)
                        elif re.match(r'^\d{1,2}[\.\/\-]\d{1,2}[\.\/\-]\d{4}$', group):
                            date_info = group
                        # Check if it's a location (port, berth, etc.)
                        elif re.match(r'^[A-Za-z\s]+$', group) and len(group.strip()) > 2:
                            location_info = group.strip()
            
            # Format time and date
            formatted_time = self._format_time_date(time_info, date_info) if time_info or date_info else None
            
            # Get context around the match
            context = self._get_context_around_match(match, text)
            
            # Calculate confidence based on match quality
            confidence = self._calculate_confidence(pattern_info, full_match, groups)
            
            event = {
                'event_type': pattern_info['type'],
                'event': pattern_info['name'],
                'confidence': confidence,
                'start_time': formatted_time,
                'location': location_info,
                'remarks': context,
                'raw_match': full_match,
                'timestamp': formatted_time,  # For sorting
                'time_raw': time_info,
                'date_raw': date_info,
                'extraction_method': 'pattern_matching'
            }
            
            return event
            
        except Exception as e:
            logger.warning(f"Error extracting event from match: {e}")
            return None
    
    def _calculate_confidence(self, pattern_info: Dict[str, Any], full_match: str, groups: Tuple) -> float:
        """Calculate confidence score for extracted event"""
        base_confidence = pattern_info['confidence']
        
        # Boost confidence if we have time/date information
        if any(groups):
            base_confidence += 0.05
        
        # Boost confidence if we have location information
        if len(groups) >= 2 and any(groups[1:]):
            base_confidence += 0.05
        
        # Reduce confidence for partial matches
        if len(full_match.strip()) < 10:
            base_confidence -= 0.10
        
        return min(1.0, max(0.0, base_confidence))
    
    def _format_time_date(self, time_str: str, date_str: str) -> str:
        """Format time and date into clean string"""
        try:
            formatted_parts = []
            
            # Format time
            if time_str:
                if len(time_str) == 4 and ':' not in time_str:  # HHMM -> HH:MM
                    time_formatted = f"{time_str[:2]}:{time_str[2:]}"
                else:
                    time_formatted = time_str
                formatted_parts.append(time_formatted)
            
            # Format date
            if date_str:
                # Convert various separators to standard format
                date_formatted = re.sub(r'[\.\/\-]', '/', date_str)
                formatted_parts.append(date_formatted)
            
            return ' '.join(formatted_parts) if formatted_parts else None
            
        except Exception as e:
            logger.warning(f"Error formatting time/date: {e}")
            return f"{time_str} {date_str}" if time_str and date_str else None
    
    def _get_context_around_match(self, match, text: str) -> str:
        """Get context around the regex match - extended to 300 words"""
        try:
            match_start = match.start()
            match_end = match.end()
            
            # Get 300 words before and after the match
            # First, get a larger character window to ensure we capture enough words
            char_window = 1000  # Start with 1000 characters to ensure we get enough words
            
            context_start = max(0, match_start - char_window)
            context_end = min(len(text), match_end + char_window)
            
            # Extract the text within the character window
            context_text = text[context_start:context_end].strip()
            
            # Split into words and get 300 words around the match
            words = context_text.split()
            match_word_start = len(text[:match_start].split())
            match_word_end = len(text[:match_end].split())
            
            # Calculate word positions relative to the context window
            relative_match_start = match_word_start - len(text[:context_start].split())
            relative_match_end = match_word_end - len(text[:context_start].split())
            
            # Get 150 words before and 150 words after the match
            words_before = max(0, relative_match_start - 150)
            words_after = min(len(words), relative_match_end + 150)
            
            # Extract the 300-word context
            context_words = words[words_before:words_after]
            context = ' '.join(context_words)
            
            # Clean up context
            context = re.sub(r'\s+', ' ', context)  # Replace multiple spaces with single space
            context = context.replace('\n', ' ')  # Replace newlines with spaces
            
            # Add context indicators
            if words_before > 0:
                context = f"... {context}"
            if words_after < len(words):
                context = f"{context} ..."
            
            return context
            
        except Exception as e:
            logger.warning(f"Error getting context: {e}")
            # Fallback: return first 500 characters if error
            return text[:500]
    
    def _enhance_events_with_context(self, events: List[Dict[str, Any]], text: str) -> List[Dict[str, Any]]:
        """Enhance events with additional context and information"""
        enhanced_events = []
        
        for event in events:
            enhanced_event = event.copy()
            
            # Try to extract vessel name if not present
            if not enhanced_event.get('vessel'):
                vessel_name = self._extract_vessel_name(text)
                if vessel_name:
                    enhanced_event['vessel'] = vessel_name
            
            # Try to extract port name if not present
            if not enhanced_event.get('port'):
                port_name = self._extract_port_name(text)
                if port_name:
                    enhanced_event['port'] = port_name
            
            # Add document metadata
            enhanced_event['document_length'] = len(text)
            enhanced_event['extraction_timestamp'] = datetime.now().isoformat()
            
            enhanced_events.append(enhanced_event)
        
        return enhanced_events
    
    def _extract_vessel_name(self, text: str) -> str:
        """Extract vessel name from text"""
        vessel_patterns = [
            r'(?i)vessel\s*[:=]\s*([A-Za-z\s\.\-]+?)(?:\n|$|IMO|FLAG)',
            r'(?i)name\s+of\s+the\s+vessel\s*[:=]\s*([A-Za-z\s\.\-]+?)(?:\n|$|IMO|FLAG)',
            r'(?i)mv\.?\s+([A-Za-z\s\.\-]+?)(?:\n|$|IMO|FLAG)',
        ]
        
        for pattern in vessel_patterns:
            match = re.search(pattern, text)
            if match:
                vessel_name = match.group(1).strip()
                if len(vessel_name) > 2:
                    return vessel_name
        
        return None
    
    def _extract_port_name(self, text: str) -> str:
        """Extract port name from text"""
        port_patterns = [
            r'(?i)port\s*[:=]\s*([A-Za-z\s\.\-]+?)(?:\n|$|TERMINAL|BERTH)',
            r'(?i)port\s+of\s+(?:loading|discharge)\s*[:=]\s*([A-Za-z\s\.\-]+?)(?:\n|$|TERMINAL|BERTH)',
        ]
        
        for pattern in port_patterns:
            match = re.search(pattern, text)
            if match:
                port_name = match.group(1).strip()
                if len(port_name) > 2:
                    return port_name
        
        return None
    
    def _remove_duplicates(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate events based on type, time, and location"""
        seen = set()
        unique_events = []
        
        for event in events:
            # Create a key based on event type, time, and location
            key = (event['event_type'], event['start_time'], event['location'])
            
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
    
    def _sort_events_by_time(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort events by timestamp if available"""
        try:
            # Filter events with valid timestamps
            events_with_time = [e for e in events if e.get('timestamp')]
            events_without_time = [e for e in events if not e.get('timestamp')]
            
            # Sort events with time by timestamp
            events_with_time.sort(key=lambda x: x['timestamp'] or '')
            
            # Return sorted events with time first, then events without time
            return events_with_time + events_without_time
            
        except Exception as e:
            logger.warning(f"Error sorting events: {e}")
            return events
    
    def get_extraction_summary(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of extracted events"""
        if not events:
            return {"message": "No events extracted"}
        
        # Count events by type
        event_counts = defaultdict(int)
        for event in events:
            event_counts[event['event_type']] += 1
        
        # Calculate average confidence
        confidences = [event.get('confidence', 0) for event in events]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Find events with highest confidence
        high_confidence_events = [e for e in events if e.get('confidence', 0) >= 0.9]
        
        return {
            "total_events": len(events),
            "event_types": dict(event_counts),
            "average_confidence": round(avg_confidence, 3),
            "high_confidence_events": len(high_confidence_events),
            "extraction_methods": list(set(e.get('extraction_method', 'unknown') for e in events)),
            "time_coverage": len([e for e in events if e.get('start_time')]),
            "location_coverage": len([e for e in events if e.get('location')])
        }

if __name__ == "__main__":
    # Test the enhanced extractor
    extractor = EnhancedMaritimeExtractor()
    
    # Test with various formats
    test_texts = [
        "VESSEL DROPPED ANCHOR 1712 HRS 16.02.2024",
        "Pilot boarded for berthing at 08:15 on 31/08/2025",
        "First line ashore berth no BB-3N at 09:30 on 31/08/2025",
        "Loading commenced on 31/08/2025 at 10:00",
        "Vessel departed Singapore on 31/08/2025 at 19:30",
        "Customs onboard at 14:30 on 31/08/2025",
        "Heavy rain caused delay in operations",
        "NOR tendered: 1806 HRS 18.02.2024",
        "Free pratique granted: 1635 HRS 18.02.2024"
    ]
    
    print("🚢 Testing Enhanced Maritime Event Extractor")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📄 Test {i}: {text}")
        events = extractor.extract_events(text)
        
        for j, event in enumerate(events):
            print(f"  Event {j+1}: {event['event']} ({event['event_type']})")
            print(f"    Time: {event['start_time']}")
            print(f"    Location: {event['location']}")
            print(f"    Confidence: {event['confidence']}")
            print(f"    Method: {event.get('extraction_method', 'unknown')}")
    
    # Test with a longer document
    print(f"\n📊 Testing with longer document...")
    long_text = """
    STATEMENT OF FACTS
    
    VESSEL: MV TEST SHIP
    IMO: 1234567
    PORT: Singapore Terminal: PSA Terminal Berth: B23
    
    VESSEL ARRIVED AT SINGAPORE PORT LIMITS: 0800 HRS 31.08.2025
    PILOT BOARDED: 0815 HRS 31.08.2025
    FIRST LINE ASHORE BERTH NO B23: 0930 HRS 31.08.2025
    ALL FAST: 0945 HRS 31.08.2025
    
    LOADING COMMENCED: 1000 HRS 31.08.2025
    LOADING COMPLETED: 1800 HRS 31.08.2025
    
    PILOT DISEMBARKED: 1900 HRS 31.08.2025
    VESSEL DEPARTED: 1930 HRS 31.08.2025
    """
    
    events = extractor.extract_events(long_text)
    summary = extractor.get_extraction_summary(events)
    
    print(f"\n📈 Extraction Summary:")
    print(f"  Total Events: {summary['total_events']}")
    print(f"  Event Types: {summary['event_types']}")
    print(f"  Average Confidence: {summary['average_confidence']}")
    print(f"  High Confidence Events: {summary['high_confidence_events']}")
    print(f"  Extraction Methods: {summary['extraction_methods']}")
