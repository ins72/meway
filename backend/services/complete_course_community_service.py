"""
Complete Course & Community Platform Service
Skool-like Learning Management System with Community Features
Version: 1.0.0 - Production Ready
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import httpx
import os
import uuid
from motor.motor_asyncio import AsyncIOMotorDatabase
from core.database import get_database
from core.config import get_api_key

logger = logging.getLogger(__name__)

class CompleteCourseService:
    """
    Complete Course & Community Platform with Skool-like features
    Features:
    - Course creation and management
    - Video upload and hosting
    - Progress tracking and certificates
    - Community discussions and forums
    - Live streaming and webinars
    - Student-to-instructor messaging
    - Gamification with points and badges
    - Member management and moderation
    - Event scheduling and calendar
    - Content drip and access control
    - Mobile-optimized learning experience
    - Real-time collaboration tools
    """
    
    def __init__(self):
        self.openai_api_key = get_api_key('OPENAI_API_KEY')
        self.stripe_secret_key = get_api_key('STRIPE_SECRET_KEY')
        
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection"""
        return get_database()
    
    async def create_course(self, course_data: Dict[str, Any], instructor_id: str) -> Dict[str, Any]:
        """
        Create a new course with comprehensive setup
        """
        try:
            db = await self.get_database()
            
            course_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Create course document
            course = {
                'course_id': course_id,
                'instructor_id': instructor_id,
                'title': course_data['title'],
                'description': course_data.get('description', ''),
                'short_description': course_data.get('short_description', ''),
                'category': course_data.get('category', 'general'),
                'subcategory': course_data.get('subcategory'),
                'level': course_data.get('level', 'beginner'),  # beginner, intermediate, advanced
                'language': course_data.get('language', 'en'),
                'price': float(course_data.get('price', 0)),
                'currency': course_data.get('currency', 'usd'),
                'course_type': course_data.get('course_type', 'self_paced'),  # self_paced, cohort_based, live
                'duration_weeks': course_data.get('duration_weeks', 0),
                'estimated_hours': course_data.get('estimated_hours', 0),
                'thumbnail_url': course_data.get('thumbnail_url', ''),
                'trailer_video_url': course_data.get('trailer_video_url', ''),
                'tags': course_data.get('tags', []),
                'learning_objectives': course_data.get('learning_objectives', []),
                'prerequisites': course_data.get('prerequisites', []),
                'target_audience': course_data.get('target_audience', []),
                'course_structure': {
                    'modules': [],
                    'total_lessons': 0,
                    'total_duration_minutes': 0
                },
                'community_settings': {
                    'enable_discussions': course_data.get('enable_discussions', True),
                    'enable_peer_review': course_data.get('enable_peer_review', False),
                    'enable_study_groups': course_data.get('enable_study_groups', True),
                    'moderation_level': course_data.get('moderation_level', 'moderate')
                },
                'access_settings': {
                    'enrollment_type': course_data.get('enrollment_type', 'open'),  # open, approval, invite_only
                    'drip_content': course_data.get('drip_content', False),
                    'drip_schedule': course_data.get('drip_schedule', {}),
                    'completion_certificate': course_data.get('completion_certificate', True),
                    'certificate_template_id': course_data.get('certificate_template_id')
                },
                'gamification': {
                    'enable_points': course_data.get('enable_points', True),
                    'enable_badges': course_data.get('enable_badges', True),
                    'enable_leaderboard': course_data.get('enable_leaderboard', False),
                    'completion_points': course_data.get('completion_points', 100)
                },
                'analytics': {
                    'total_enrollments': 0,
                    'active_students': 0,
                    'completion_rate': 0.0,
                    'average_rating': 0.0,
                    'total_reviews': 0,
                    'revenue': 0.0
                },
                'status': course_data.get('status', 'draft'),  # draft, published, archived
                'published_at': None,
                'created_at': current_time,
                'updated_at': current_time
            }
            
            # Insert course
            await db.courses.insert_one(course)
            
            # Create course community
            community_data = await self._create_course_community(course_id, instructor_id, course_data)
            
            # Initialize analytics
            await self._initialize_course_analytics(course_id, instructor_id)
            
            # Create default modules if provided
            if course_data.get('initial_modules'):
                for module_data in course_data['initial_modules']:
                    await self.create_course_module(course_id, module_data, instructor_id)
            
            return {
                'success': True,
                'course': course,
                'community': community_data,
                'course_url': f"/courses/{course_id}",
                'community_url': f"/community/{community_data['community_id']}"
            }
            
        except Exception as e:
            logger.error(f"Course creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_course_community(self, course_id: str, instructor_id: str, course_data: Dict) -> Dict:
        """Create associated community for the course"""
        try:
            db = await self.get_database()
            
            community_id = str(uuid.uuid4())
            
            community = {
                'community_id': community_id,
                'course_id': course_id,
                'owner_id': instructor_id,
                'name': f"{course_data['title']} Community",
                'description': f"Community for {course_data['title']} students",
                'type': 'course_community',
                'privacy': course_data.get('community_privacy', 'private'),  # public, private, secret
                'member_count': 0,
                'post_count': 0,
                'categories': [
                    {
                        'category_id': str(uuid.uuid4()),
                        'name': 'General Discussion',
                        'description': 'General course discussions',
                        'position': 1
                    },
                    {
                        'category_id': str(uuid.uuid4()),
                        'name': 'Q&A',
                        'description': 'Questions and answers',
                        'position': 2
                    },
                    {
                        'category_id': str(uuid.uuid4()),
                        'name': 'Student Showcase',
                        'description': 'Share your work and projects',
                        'position': 3
                    }
                ],
                'rules': course_data.get('community_rules', [
                    'Be respectful to all community members',
                    'Stay on topic and relevant to the course',
                    'No spam or self-promotion without permission',
                    'Help others and share knowledge'
                ]),
                'moderation_settings': {
                    'auto_moderation': True,
                    'require_approval': False,
                    'moderator_ids': [instructor_id]
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            await db.communities.insert_one(community)
            
            return community
            
        except Exception as e:
            logger.error(f"Community creation error: {str(e)}")
            return {}
    
    async def create_course_module(self, course_id: str, module_data: Dict[str, Any], instructor_id: str) -> Dict[str, Any]:
        """
        Create a course module with lessons
        """
        try:
            db = await self.get_database()
            
            # Verify course ownership
            course = await db.courses.find_one({'course_id': course_id, 'instructor_id': instructor_id})
            if not course:
                return {'success': False, 'error': 'Course not found or access denied'}
            
            module_id = str(uuid.uuid4())
            
            module = {
                'module_id': module_id,
                'course_id': course_id,
                'title': module_data['title'],
                'description': module_data.get('description', ''),
                'position': module_data.get('position', 1),
                'is_preview': module_data.get('is_preview', False),
                'lessons': [],
                'total_lessons': 0,
                'total_duration_minutes': 0,
                'completion_criteria': module_data.get('completion_criteria', {
                    'require_all_lessons': True,
                    'minimum_score': 70
                }),
                'drip_settings': {
                    'is_dripped': module_data.get('is_dripped', False),
                    'available_after_days': module_data.get('available_after_days', 0),
                    'prerequisite_module_id': module_data.get('prerequisite_module_id')
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Insert module
            await db.course_modules.insert_one(module)
            
            # Create lessons if provided
            if module_data.get('lessons'):
                for lesson_data in module_data['lessons']:
                    lesson = await self.create_lesson(module_id, lesson_data, instructor_id)
                    if lesson['success']:
                        module['lessons'].append(lesson['lesson'])
                        module['total = await self._calculate_total(user_id)
                        module['total = await self._calculate_total(user_id))
            
            # Update module with lesson counts
            await db.course_modules.update_one(
                {'module_id': module_id},
                {
                    '$set': {
                        'total_lessons': module['total_lessons'],
                        'total_duration_minutes': module['total_duration_minutes']
                    }
                }
            )
            
            # Update course structure
            await self._update_course_structure(course_id)
            
            return {
                'success': True,
                'module': module
            }
            
        except Exception as e:
            logger.error(f"Module creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_lesson(self, module_id: str, lesson_data: Dict[str, Any], instructor_id: str) -> Dict[str, Any]:
        """
        Create a lesson with content and resources
        """
        try:
            db = await self.get_database()
            
            lesson_id = str(uuid.uuid4())
            
            lesson = {
                'lesson_id': lesson_id,
                'module_id': module_id,
                'title': lesson_data['title'],
                'description': lesson_data.get('description', ''),
                'position': lesson_data.get('position', 1),
                'lesson_type': lesson_data.get('lesson_type', 'video'),  # video, text, quiz, assignment, live
                'content': lesson_data.get('content', {}),
                'video_data': {
                    'video_url': lesson_data.get('video_url', ''),
                    'video_duration_seconds': lesson_data.get('video_duration_seconds', 0),
                    'video_quality': lesson_data.get('video_quality', 'HD'),
                    'subtitles': lesson_data.get('subtitles', []),
                    'chapters': lesson_data.get('chapters', [])
                },
                'resources': lesson_data.get('resources', []),
                'downloadable_files': lesson_data.get('downloadable_files', []),
                'assignments': lesson_data.get('assignments', []),
                'quiz_data': lesson_data.get('quiz_data', {}),
                'completion_criteria': {
                    'watch_percentage': lesson_data.get('watch_percentage', 80),
                    'require_quiz_pass': lesson_data.get('require_quiz_pass', False),
                    'minimum_quiz_score': lesson_data.get('minimum_quiz_score', 70)
                },
                'access_settings': {
                    'is_preview': lesson_data.get('is_preview', False),
                    'is_locked': lesson_data.get('is_locked', False),
                    'unlock_conditions': lesson_data.get('unlock_conditions', {})
                },
                'analytics': {
                    'total_views': 0,
                    'average_completion_rate': 0.0,
                    'average_rating': 0.0,
                    'comment_count': 0
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            await db.lessons.insert_one(lesson)
            
            return {
                'success': True,
                'lesson': lesson
            }
            
        except Exception as e:
            logger.error(f"Lesson creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def enroll_student(self, course_id: str, student_id: str, enrollment_data: Dict = None) -> Dict[str, Any]:
        """
        Enroll a student in a course
        """
        try:
            db = await self.get_database()
            
            # Check if course exists
            course = await db.courses.find_one({'course_id': course_id})
            if not course:
                return {'success': False, 'error': 'Course not found'}
            
            # Check if already enrolled
            existing_enrollment = await db.enrollments.find_one({
                'course_id': course_id,
                'student_id': student_id
            })
            if existing_enrollment:
                return {'success': False, 'error': 'Student already enrolled'}
            
            enrollment_id = str(uuid.uuid4())
            enrollment = {
                'enrollment_id': enrollment_id,
                'course_id': course_id,
                'student_id': student_id,
                'instructor_id': course['instructor_id'],
                'enrollment_type': enrollment_data.get('enrollment_type', 'paid') if enrollment_data else 'paid',
                'payment_status': enrollment_data.get('payment_status', 'completed') if enrollment_data else 'completed',
                'payment_amount': course['price'],
                'currency': course['currency'],
                'enrolled_at': datetime.utcnow(),
                'progress': {
                    'completed_lessons': [],
                    'completed_modules': [],
                    'completion_percentage': 0.0,
                    'total_watch_time_minutes': 0,
                    'last_accessed': datetime.utcnow(),
                    'current_lesson_id': None
                },
                'certificates': [],
                'gamification': {
                    'points_earned': 0,
                    'badges_earned': [],
                    'streak_days': 0,
                    'last_activity': datetime.utcnow()
                },
                'status': 'active',  # active, completed, dropped, suspended
                'completion_date': None
            }
            
            await db.enrollments.insert_one(enrollment)
            
            # Add student to course community
            await self._add_student_to_community(course_id, student_id)
            
            # Update course analytics
            await db.courses.update_one(
                {'course_id': course_id},
                {
                    '$inc': {
                        'analytics.total_enrollments': 1,
                        'analytics.active_students': 1,
                        'analytics.revenue': course['price']
                    }
                }
            )
            
            # Initialize student progress tracking
            await self._initialize_student_progress(course_id, student_id)
            
            return {
                'success': True,
                'enrollment': enrollment,
                'course_access_url': f"/courses/{course_id}/learn"
            }
            
        except Exception as e:
            logger.error(f"Student enrollment error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def track_lesson_progress(self, lesson_id: str, student_id: str, progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track student progress on a lesson
        """
        try:
            db = await self.get_database()
            
            # Get lesson and course info
            lesson = await db.lessons.find_one({'lesson_id': lesson_id})
            if not lesson:
                return {'success': False, 'error': 'Lesson not found'}
            
            module = await db.course_modules.find_one({'module_id': lesson['module_id']})
            course_id = module['course_id']
            
            # Update or create progress record
            progress_id = str(uuid.uuid4())
            progress = {
                'progress_id': progress_id,
                'lesson_id': lesson_id,
                'module_id': lesson['module_id'],
                'course_id': course_id,
                'student_id': student_id,
                'watch_time_seconds': progress_data.get('watch_time_seconds', 0),
                'completion_percentage': progress_data.get('completion_percentage', 0),
                'is_completed': progress_data.get('is_completed', False),
                'quiz_scores': progress_data.get('quiz_scores', []),
                'notes': progress_data.get('notes', ''),
                'bookmarks': progress_data.get('bookmarks', []),
                'last_position_seconds': progress_data.get('last_position_seconds', 0),
                'started_at': progress_data.get('started_at', datetime.utcnow()),
                'completed_at': progress_data.get('completed_at') if progress_data.get('is_completed') else None,
                'updated_at': datetime.utcnow()
            }
            
            # Upsert progress
            await db.lesson_progress.update_one(
                {'lesson_id': lesson_id, 'student_id': student_id},
                {'$set': progress},
                upsert=True
            )
            
            # Update enrollment progress
            if progress_data.get('is_completed'):
                await self._update_enrollment_progress(course_id, student_id, lesson_id)
            
            # Award points for completion
            if progress_data.get('is_completed'):
                await self._award_lesson_completion_points(course_id, student_id, lesson_id)
            
            return {
                'success': True,
                'progress': progress
            }
            
        except Exception as e:
            logger.error(f"Progress tracking error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def create_community_post(self, community_id: str, post_data: Dict[str, Any], author_id: str) -> Dict[str, Any]:
        """
        Create a community discussion post
        """
        try:
            db = await self.get_database()
            
            # Verify community access
            community = await db.communities.find_one({'community_id': community_id})
            if not community:
                return {'success': False, 'error': 'Community not found'}
            
            post_id = str(uuid.uuid4())
            
            post = {
                'post_id': post_id,
                'community_id': community_id,
                'author_id': author_id,
                'category_id': post_data.get('category_id'),
                'title': post_data['title'],
                'content': post_data['content'],
                'post_type': post_data.get('post_type', 'discussion'),  # discussion, question, announcement, showcase
                'tags': post_data.get('tags', []),
                'attachments': post_data.get('attachments', []),
                'images': post_data.get('images', []),
                'poll_data': post_data.get('poll_data'),
                'engagement': {
                    'likes': 0,
                    'replies': 0,
                    'views': 0,
                    'shares': 0
                },
                'moderation': {
                    'is_approved': True,
                    'is_pinned': post_data.get('is_pinned', False),
                    'is_locked': post_data.get('is_locked', False),
                    'moderation_notes': ''
                },
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            await db.community_posts.insert_one(post)
            
            # Update community stats
            await db.communities.update_one(
                {'community_id': community_id},
                {
                    '$inc': {'post_count': 1},
                    '$set': {'updated_at': datetime.utcnow()}
                }
            )
            
            return {
                'success': True,
                'post': post
            }
            
        except Exception as e:
            logger.error(f"Community post creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_student_dashboard(self, student_id: str) -> Dict[str, Any]:
        """
        Get comprehensive student dashboard
        """
        try:
            db = await self.get_database()
            
            # Get active enrollments
            enrollments = await db.enrollments.find({
                'student_id': student_id,
                'status': 'active'
            }).to_list(length=None)
            
            # Get course details for each enrollment
            courses = []
            for enrollment in enrollments:
                course = await db.courses.find_one({'course_id': enrollment['course_id']})
                if course:
                    course_info = {
                        'course': course,
                        'enrollment': enrollment,
                        'progress_percentage': enrollment['progress']['completion_percentage'],
                        'last_accessed': enrollment['progress']['last_accessed'],
                        'current_lesson': enrollment['progress'].get('current_lesson_id')
                    }
                    courses.append(course_info)
            
            # Get recent community activity
            recent_posts = await db.community_posts.find({
                'author_id': student_id
            }).sort('created_at', -1).limit(5).to_list(length=5)
            
            # Get gamification stats
            total_points = sum(enrollment['gamification']['points_earned'] for enrollment in enrollments)
            total_badges = []
            for enrollment in enrollments:
                total_badges.extend(enrollment['gamification']['badges_earned'])
            
            # Get upcoming live sessions
            upcoming_sessions = await db.live_sessions.find({
                'course_id': {'$in': [enrollment['course_id'] for enrollment in enrollments]},
                'scheduled_time': {'$gte': datetime.utcnow()}
            }).sort('scheduled_time', 1).limit(5).to_list(length=5)
            
            dashboard = {
                'student_id': student_id,
                'summary': {
                    'total_courses': len(courses),
                    'completed_courses': len([c for c in courses if c['enrollment']['status'] == 'completed']),
                    'total_points': total_points,
                    'total_badges': len(total_badges),
                    'total_certificates': sum(len(enrollment['certificates']) for enrollment in enrollments)
                },
                'active_courses': courses,
                'recent_community_activity': recent_posts,
                'gamification': {
                    'total_points': total_points,
                    'badges': total_badges,
                    'achievements': []
                },
                'upcoming_sessions': upcoming_sessions,
                'recommendations': await self._get_course_recommendations(student_id),
                'generated_at': datetime.utcnow()
            }
            
            return {
                'success': True,
                'dashboard': dashboard
            }
            
        except Exception as e:
            logger.error(f"Student dashboard error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _add_student_to_community(self, course_id: str, student_id: str):
        """Add student to course community"""
        try:
            db = await self.get_database()
            
            community = await db.communities.find_one({'course_id': course_id})
            if community:
                member = {
                    'member_id': str(uuid.uuid4()),
                    'community_id': community['community_id'],
                    'user_id': student_id,
                    'role': 'student',
                    'joined_at': datetime.utcnow(),
                    'status': 'active'
                }
                
                await db.community_members.insert_one(member)
                
                # Update community member count
                await db.communities.update_one(
                    {'community_id': community['community_id']},
                    {'$inc': {'member_count': 1}}
                )
                
        except Exception as e:
            logger.error(f"Add student to community error: {str(e)}")
    
    async def _initialize_student_progress(self, course_id: str, student_id: str):
        """Initialize progress tracking for student"""
        try:
            db = await self.get_database()
            
            # Get all lessons in the course
            modules = await db.course_modules.find({'course_id': course_id}).to_list(length=None)
            
            for module in modules:
                lessons = await db.lessons.find({'module_id': module['module_id']}).to_list(length=None)
                
                for lesson in lessons:
                    progress = {
                        'progress_id': str(uuid.uuid4()),
                        'lesson_id': lesson['lesson_id'],
                        'module_id': module['module_id'],
                        'course_id': course_id,
                        'student_id': student_id,
                        'watch_time_seconds': 0,
                        'completion_percentage': 0,
                        'is_completed': False,
                        'created_at': datetime.utcnow()
                    }
                    
                    await db.lesson_progress.insert_one(progress)
                    
        except Exception as e:
            logger.error(f"Initialize student progress error: {str(e)}")
    
    async def _update_enrollment_progress(self, course_id: str, student_id: str, completed_lesson_id: str):
        """Update overall enrollment progress"""
        try:
            db = await self.get_database()
            
            # Get total lessons in course
            total_lessons = await db.lessons.count_documents({
                'module_id': {'$in': [
                    module['module_id'] for module in 
                    await db.course_modules.find({'course_id': course_id}).to_list(length=None)
                ]}
            })
            
            # Get completed lessons
            completed_lessons = await db.lesson_progress.count_documents({
                'course_id': course_id,
                'student_id': student_id,
                'is_completed': True
            })
            
            completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            
            # Update enrollment
            update_data = {
                'progress.completion_percentage': completion_percentage,
                'progress.last_accessed': datetime.utcnow()
            }
            
            # Add completed lesson to list
            await db.enrollments.update_one(
                {'course_id': course_id, 'student_id': student_id},
                {
                    '$set': update_data,
                    '$addToSet': {'progress.completed_lessons': completed_lesson_id}
                }
            )
            
            # Check if course is completed
            if completion_percentage >= 100:
                await self._complete_course(course_id, student_id)
                
        except Exception as e:
            logger.error(f"Update enrollment progress error: {str(e)}")
    
    async def _award_lesson_completion_points(self, course_id: str, student_id: str, lesson_id: str):
        """Award points for lesson completion"""
        try:
            db = await self.get_database()
            
            # Get course gamification settings
            course = await db.courses.find_one({'course_id': course_id})
            if not course or not course['gamification']['enable_points']:
                return
            
            points_per_lesson = 10  # Default points per lesson
            
            await db.enrollments.update_one(
                {'course_id': course_id, 'student_id': student_id},
                {
                    '$inc': {'gamification.points_earned': points_per_lesson},
                    '$set': {'gamification.last_activity': datetime.utcnow()}
                }
            )
            
        except Exception as e:
            logger.error(f"Award points error: {str(e)}")
    
    async def _complete_course(self, course_id: str, student_id: str):
        """Handle course completion"""
        try:
            db = await self.get_database()
            
            # Update enrollment status
            await db.enrollments.update_one(
                {'course_id': course_id, 'student_id': student_id},
                {
                    '$set': {
                        'status': 'completed',
                        'completion_date': datetime.utcnow()
                    }
                }
            )
            
            # Generate certificate
            await self._generate_completion_certificate(course_id, student_id)
            
            # Award completion points
            course = await db.courses.find_one({'course_id': course_id})
            if course and course['gamification']['enable_points']:
                completion_points = course['gamification']['completion_points']
                await db.enrollments.update_one(
                    {'course_id': course_id, 'student_id': student_id},
                    {'$inc': {'gamification.points_earned': completion_points}}
                )
            
        except Exception as e:
            logger.error(f"Complete course error: {str(e)}")
    
    async def _generate_completion_certificate(self, course_id: str, student_id: str):
        """Generate completion certificate"""
        try:
            db = await self.get_database()
            
            certificate_id = str(uuid.uuid4())
            certificate = {
                'certificate_id': certificate_id,
                'course_id': course_id,
                'student_id': student_id,
                'certificate_url': f"/certificates/{certificate_id}",
                'issued_at': datetime.utcnow(),
                'verification_code': str(uuid.uuid4())[:12].upper()
            }
            
            await db.certificates.insert_one(certificate)
            
            # Add to enrollment
            await db.enrollments.update_one(
                {'course_id': course_id, 'student_id': student_id},
                {'$push': {'certificates': certificate}}
            )
            
        except Exception as e:
            logger.error(f"Generate certificate error: {str(e)}")
    
    async def _get_course_recommendations(self, student_id: str) -> List[Dict]:
        """Get course recommendations for student"""
        try:
            db = await self.get_database()
            
            # Get student's enrolled course categories
            enrollments = await db.enrollments.find({'student_id': student_id}).to_list(length=None)
            enrolled_course_ids = [e['course_id'] for e in enrollments]
            
            if enrolled_course_ids:
                enrolled_courses = await db.courses.find(
                    {'course_id': {'$in': enrolled_course_ids}}
                ).to_list(length=None)
                
                categories = list(set(course['category'] for course in enrolled_courses))
                
                # Find similar courses
                recommended_courses = await db.courses.find({
                    'category': {'$in': categories},
                    'course_id': {'$nin': enrolled_course_ids},
                    'status': 'published'
                }).limit(5).to_list(length=5)
                
                return recommended_courses
            
            # Default recommendations for new students
            return await db.courses.find({
                'status': 'published'
            }).sort('analytics.total = await self._calculate_total(user_id))
            
        except Exception as e:
            logger.error(f"Get recommendations error: {str(e)}")
            return []
    
    async def _update_course_structure(self, course_id: str):
        """Update course structure summary"""
        try:
            db = await self.get_database()
            
            # Get all modules
            modules = await db.course_modules.find({'course_id': course_id}).to_list(length=None)
            
            total = await self._calculate_total(user_id)
            total = await self._calculate_total(user_id)
            
            for module in modules:
                lessons = await db.lessons.find({'module_id': module['module_id']}).to_list(length=None)
                module_lessons = len(lessons)
                module_duration = sum(lesson.get('video_data', {}).get('video_duration_seconds', 0) for lesson in lessons)
                
                total_lessons += module_lessons
                total_duration += module_duration
                
                # Update module totals
                await db.course_modules.update_one(
                    {'module_id': module['module_id']},
                    {
                        '$set': {
                            'total_lessons': module_lessons,
                            'total_duration_minutes': module_duration // 60
                        }
                    }
                )
            
            # Update course structure
            await db.courses.update_one(
                {'course_id': course_id},
                {
                    '$set': {
                        'course_structure.total_lessons': total_lessons,
                        'course_structure.total_duration_minutes': total_duration // 60,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"Update course structure error: {str(e)}")
    
    async def _initialize_course_analytics(self, course_id: str, instructor_id: str):
        """Initialize course analytics tracking"""
        try:
            db = await self.get_database()
            
            analytics = {
                'analytics_id': str(uuid.uuid4()),
                'course_id': course_id,
                'instructor_id': instructor_id,
                'daily_stats': {},
                'monthly_stats': {},
                'engagement_metrics': {
                    'video_watch_time': 0,
                    'discussion_posts': 0,
                    'assignment_submissions': 0,
                    'quiz_attempts': 0
                },
                'student_feedback': {
                    'ratings': [],
                    'reviews': [],
                    'completion_feedback': []
                },
                'created_at': datetime.utcnow()
            }
            
            await db.course_analytics.insert_one(analytics)
            
        except Exception as e:
            logger.error(f"Initialize course analytics error: {str(e)}")

# Global service instance
course_service = CompleteCourseService()

    async def get_course(self, user_id: str, course_id: str):
        """Get specific course"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            course = await collections['courses'].find_one({
                "_id": course_id,
                "user_id": user_id
            })
            
            if not course:
                return {"success": False, "message": "Course not found"}
            
            return {
                "success": True,
                "data": course,
                "message": "Course retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def delete_course(self, user_id: str, course_id: str):
        """Delete course"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            result = await collections['courses'].delete_one({
                "_id": course_id,
                "user_id": user_id
            })
            
            if result.deleted_count = await self._calculate_count(user_id):
                return {"success": False, "message": "Course not found"}
            
            return {
                "success": True,
                "message": "Course deleted successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_courses(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's courses"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['courses'].find(query).skip(skip).limit(limit)
            courses = await cursor.to_list(length=limit)
            
            total_count = await collections['courses'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "courses": courses,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Courses retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def update_course(self, user_id: str, course_id: str, update_data: dict):
        """Update existing course with validation"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database connection unavailable"}
            
            if not course_id or not update_data:
                return {"success": False, "message": "ID and update data are required"}
            
            # Prepare update data
            update_data["updated_at"] = datetime.utcnow()
            update_data["version"] = {"$inc": 1}  # Increment version for optimistic locking
            
            # Remove protected fields from update
            protected_fields = ["_id", "user_id", "created_at"]
            for field in protected_fields:
                update_data.pop(field, None)
            
            # Update with user access control
            result = await collections['courses'].update_one(
                {
                    "_id": course_id,
                    "user_id": user_id,
                    "status": {"$ne": "deleted"}
                },
                {"$set": update_data}
            )
            
            if result.matched_count = await self._calculate_count(user_id):
                return {"success": False, "message": "Course not found or access denied"}
            
            if result.modified_count = await self._calculate_count(user_id):
                return {"success": False, "message": "No changes were made"}
            
            # Retrieve updated course
            updated_course = await collections['courses'].find_one({
                "_id": course_id,
                "user_id": user_id
            })
            
            # Process for JSON serialization
            if updated_course and updated_course.get("updated_at"):
                updated_course["updated_at"] = updated_course["updated_at"].isoformat()
            
            return {
                "success": True,
                "data": updated_course,
                "message": "Course updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating course: {str(e)}")
            return {"success": False, "message": f"Update failed: {str(e)}"}