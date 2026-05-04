"""
Route Service Layer
Business logic for train route management
"""
from app.db import Database
from app.queries.route_queries import *
from datetime import datetime


class RouteService:
    """Service for managing route operations"""
    
    @staticmethod
    def get_route(route_id):
        """Get a single route by ID"""
        try:
            return Database.fetch_one(GET_ROUTE, (route_id,))
        except Exception as e:
            raise Exception(f"Failed to fetch route: {str(e)}")
    
    @staticmethod
    def get_route_details(route_id):
        """Get full route details with train and station info"""
        try:
            return Database.fetch_one(GET_ROUTE_DETAILS, (route_id,))
        except Exception as e:
            raise Exception(f"Failed to fetch route details: {str(e)}")
    
    @staticmethod
    def list_routes(page=1, limit=20):
        """List all routes with pagination"""
        try:
            offset = (page - 1) * limit
            routes = Database.fetch_all(LIST_ROUTES, (limit, offset))
            total = Database.fetch_scalar(COUNT_ROUTES)
            
            return {
                'data': routes,
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        except Exception as e:
            raise Exception(f"Failed to list routes: {str(e)}")
    
    @staticmethod
    def create_route(train_id, source_station_id, destination_station_id, distance, estimated_duration):
        """
        Create a new route with validation
        
        Args:
            train_id: Train ID
            source_station_id: Source station ID
            destination_station_id: Destination station ID
            distance: Distance in km
            estimated_duration: Estimated duration in hours
        
        Returns:
            Dict with success status and route_id or error
        """
        try:
            # Validate inputs
            if not all([train_id, source_station_id, destination_station_id, distance, estimated_duration]):
                return {'success': False, 'error': 'All fields are required'}
            
            # Validate source and destination are different
            if source_station_id == destination_station_id:
                return {'success': False, 'error': 'Source and destination stations must be different'}
            
            # Validate train exists
            train = Database.fetch_one("SELECT train_id FROM trains WHERE train_id = %s", (train_id,))
            if not train:
                return {'success': False, 'error': 'Train not found'}
            
            # Validate source station exists
            source_station = Database.fetch_one(
                "SELECT station_id FROM stations WHERE station_id = %s",
                (source_station_id,)
            )
            if not source_station:
                return {'success': False, 'error': 'Source station not found'}
            
            # Validate destination station exists
            dest_station = Database.fetch_one(
                "SELECT station_id FROM stations WHERE station_id = %s",
                (destination_station_id,)
            )
            if not dest_station:
                return {'success': False, 'error': 'Destination station not found'}
            
            # Validate distance is positive
            try:
                distance = float(distance)
                if distance <= 0:
                    return {'success': False, 'error': 'Distance must be greater than 0'}
            except (ValueError, TypeError):
                return {'success': False, 'error': 'Distance must be a valid number'}
            
            # Validate estimated duration is positive
            try:
                estimated_duration = float(estimated_duration)
                if estimated_duration <= 0:
                    return {'success': False, 'error': 'Estimated duration must be greater than 0'}
            except (ValueError, TypeError):
                return {'success': False, 'error': 'Estimated duration must be a valid number'}
            
            # Check if route already exists
            existing_route = Database.fetch_one(
                """SELECT route_id FROM routes 
                   WHERE train_id = %s AND source_station_id = %s AND destination_station_id = %s""",
                (train_id, source_station_id, destination_station_id)
            )
            if existing_route:
                return {'success': False, 'error': 'This route already exists for this train'}
            
            # Create route
            route_id = Database.execute_returning(
                CREATE_ROUTE,
                (train_id, source_station_id, destination_station_id, distance, estimated_duration)
            )
            
            if route_id:
                return {'success': True, 'route_id': route_id}
            else:
                return {'success': False, 'error': 'Failed to create route'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_route(route_id, distance=None, estimated_duration=None):
        """
        Update route distance and/or estimated duration
        
        Args:
            route_id: Route ID
            distance: New distance (optional)
            estimated_duration: New estimated duration (optional)
        
        Returns:
            Dict with success status
        """
        try:
            # Validate route exists
            route = RouteService.get_route(route_id)
            if not route:
                return {'success': False, 'error': 'Route not found'}
            
            # Check if schedules exist for this route
            schedule_count = Database.fetch_scalar(
                "SELECT COUNT(*) FROM schedules WHERE route_id = %s AND schedule_status IN ('Active', 'confirmed')",
                (route_id,)
            )
            
            if schedule_count and schedule_count > 0:
                return {'success': False, 'error': f'Cannot modify route with {schedule_count} active schedules'}
            
            # Validate values if provided
            if distance is not None:
                try:
                    distance = float(distance)
                    if distance <= 0:
                        return {'success': False, 'error': 'Distance must be greater than 0'}
                except (ValueError, TypeError):
                    return {'success': False, 'error': 'Distance must be a valid number'}
            else:
                distance = route['distance']
            
            if estimated_duration is not None:
                try:
                    estimated_duration = float(estimated_duration)
                    if estimated_duration <= 0:
                        return {'success': False, 'error': 'Estimated duration must be greater than 0'}
                except (ValueError, TypeError):
                    return {'success': False, 'error': 'Estimated duration must be a valid number'}
            else:
                estimated_duration = route['estimated_duration']
            
            # Update route
            affected = Database.execute(
                UPDATE_ROUTE,
                (distance, estimated_duration, route_id)
            )
            
            if affected > 0:
                return {'success': True, 'message': 'Route updated successfully'}
            else:
                return {'success': False, 'error': 'Failed to update route'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_route(route_id):
        """
        Delete a route (only if no active schedules)
        
        Args:
            route_id: Route ID
        
        Returns:
            Dict with success status
        """
        try:
            # Validate route exists
            route = RouteService.get_route(route_id)
            if not route:
                return {'success': False, 'error': 'Route not found'}
            
            # Check if schedules exist for this route
            schedule_count = Database.fetch_scalar(
                "SELECT COUNT(*) FROM schedules WHERE route_id = %s",
                (route_id,)
            )
            
            if schedule_count and schedule_count > 0:
                return {'success': False, 'error': f'Cannot delete route with {schedule_count} schedules. Cancel the schedules first.'}
            
            # Delete route
            affected = Database.execute(DELETE_ROUTE, (route_id,))
            
            if affected > 0:
                return {'success': True, 'message': 'Route deleted successfully'}
            else:
                return {'success': False, 'error': 'Failed to delete route'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def find_routes_between_stations(source_station_id, destination_station_id):
        """
        Find all routes between two stations
        
        Args:
            source_station_id: Source station ID
            destination_station_id: Destination station ID
        
        Returns:
            List of matching routes
        """
        try:
            # Validate stations exist
            source_station = Database.fetch_one(
                "SELECT station_id FROM stations WHERE station_id = %s",
                (source_station_id,)
            )
            if not source_station:
                raise Exception("Source station not found")
            
            dest_station = Database.fetch_one(
                "SELECT station_id FROM stations WHERE station_id = %s",
                (destination_station_id,)
            )
            if not dest_station:
                raise Exception("Destination station not found")
            
            # Find routes
            routes = Database.fetch_all(
                FIND_ROUTES_BETWEEN_STATIONS,
                (source_station_id, destination_station_id)
            )
            
            return routes
        
        except Exception as e:
            raise Exception(f"Failed to find routes: {str(e)}")
    
    @staticmethod
    def get_routes_for_train(train_id):
        """
        Get all routes assigned to a specific train
        
        Args:
            train_id: Train ID
        
        Returns:
            List of routes for the train
        """
        try:
            # Validate train exists
            train = Database.fetch_one(
                "SELECT train_id FROM trains WHERE train_id = %s",
                (train_id,)
            )
            if not train:
                raise Exception("Train not found")
            
            # Get routes
            routes = Database.fetch_all(GET_ROUTES_FOR_TRAIN, (train_id,))
            
            return routes
        
        except Exception as e:
            raise Exception(f"Failed to fetch routes for train: {str(e)}")
    
    @staticmethod
    def get_route_statistics(route_id):
        """
        Get statistics for a route (schedules, bookings, revenue)
        
        Args:
            route_id: Route ID
        
        Returns:
            Dict with statistics
        """
        try:
            # Get route details
            route = RouteService.get_route_details(route_id)
            if not route:
                raise Exception("Route not found")
            
            # Get schedule count
            schedule_count = Database.fetch_scalar(
                "SELECT COUNT(*) FROM schedules WHERE route_id = %s",
                (route_id,)
            )
            
            # Get total bookings on this route
            booking_data = Database.fetch_one(
                """SELECT COUNT(*) as total_bookings, 
                          SUM(CASE WHEN booking_status != 'cancelled' THEN 1 ELSE 0 END) as active_bookings
                   FROM bookings b
                   JOIN schedules s ON b.schedule_id = s.schedule_id
                   WHERE s.route_id = %s""",
                (route_id,)
            )
            
            # Get revenue for this route
            revenue = Database.fetch_scalar(
                """SELECT SUM(p.payment_amount) as total_revenue
                   FROM payments p
                   JOIN bookings b ON p.booking_id = b.booking_id
                   JOIN schedules s ON b.schedule_id = s.schedule_id
                   WHERE s.route_id = %s AND p.payment_status = 'completed'""",
                (route_id,)
            )
            
            # Get average occupancy
            occupancy = Database.fetch_one(
                """SELECT AVG((COUNT(b.booking_id)::float / t.capacity) * 100) as avg_occupancy
                   FROM schedules s
                   JOIN trains t ON s.train_id = t.train_id
                   LEFT JOIN bookings b ON s.schedule_id = b.schedule_id AND b.booking_status != 'cancelled'
                   WHERE s.route_id = %s
                   GROUP BY s.route_id""",
                (route_id,)
            )
            
            return {
                'route': route,
                'schedule_count': schedule_count or 0,
                'total_bookings': booking_data['total_bookings'] if booking_data else 0,
                'active_bookings': booking_data['active_bookings'] if booking_data else 0,
                'total_revenue': revenue or 0,
                'average_occupancy': occupancy['avg_occupancy'] if occupancy else 0
            }
        
        except Exception as e:
            raise Exception(f"Failed to fetch route statistics: {str(e)}")
    
    @staticmethod
    def search_routes(train_id=None, source_station_id=None, destination_station_id=None, page=1, limit=20):
        """
        Search routes with optional filters
        
        Args:
            train_id: Filter by train (optional)
            source_station_id: Filter by source station (optional)
            destination_station_id: Filter by destination station (optional)
            page: Page number for pagination
            limit: Items per page
        
        Returns:
            Dict with filtered routes and pagination info
        """
        try:
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if train_id:
                where_conditions.append("r.train_id = %s")
                params.append(train_id)
            
            if source_station_id:
                where_conditions.append("r.source_station_id = %s")
                params.append(source_station_id)
            
            if destination_station_id:
                where_conditions.append("r.destination_station_id = %s")
                params.append(destination_station_id)
            
            # Build base query
            base_query = """
                SELECT r.route_id, r.train_id, r.source_station_id, r.destination_station_id, 
                       r.distance, r.estimated_duration,
                       t.train_name, t.train_number,
                       st_src.station_name as source_station,
                       st_dst.station_name as destination_station
                FROM routes r
                JOIN trains t ON r.train_id = t.train_id
                JOIN stations st_src ON r.source_station_id = st_src.station_id
                JOIN stations st_dst ON r.destination_station_id = st_dst.station_id
            """
            
            if where_conditions:
                base_query += " WHERE " + " AND ".join(where_conditions)
            
            base_query += " ORDER BY r.route_id LIMIT %s OFFSET %s"
            offset = (page - 1) * limit
            params.extend([limit, offset])
            
            # Execute search
            routes = Database.fetch_all(base_query, params)
            
            # Get total count
            count_query = "SELECT COUNT(*) FROM routes r"
            if where_conditions:
                count_query += " WHERE " + " AND ".join(where_conditions[:len(where_conditions)])
            
            total = Database.fetch_scalar(count_query, params[:-2] if params else []) or 0
            
            return {
                'data': routes,
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        
        except Exception as e:
            raise Exception(f"Search failed: {str(e)}")