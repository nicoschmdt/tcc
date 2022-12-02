import similarity

from ..utils.trajetoria import process_trajectories, Trajectory, Point
from enum import Enum, auto

# t-closeness: distribuição igual de PoI
# l-diversity: every point has at least l categories
class PoiCategory(Enum):
    Entertainment = auto()
    Education = auto()
    Scenery = auto()
    Business = auto()
    Industry = auto()
    Residence = auto()
    Transport = auto()

@dataclass
class TuPoint:
    name: str
    user_id: str
    category: set[PoiCategory]
    latitude: float
    longitude: float
    utc_timestamp: datetime
    duration: float

@dataclass
class TuTrajectory:
    trajectory: List[Point]
    n: int = 1

def get_venue_category(trajectories: list[Trajectory]) -> list[TuTrajectory]:
    altered_trajectories = []

    for trajectory in trajectories:
        tu_trajectory = TuTrajectory([])
        for point in trajectory.trajectory:
            tu_point = modify_point(point)
            tu_trajectory.trajectory.append(tu_point)

        altered_trajectories.append(tu_trajectory)

    return altered_trajectories

def modify_point(point: Point) -> TuPoint:
    return TuPoint(
        point.name,
        point.user_id,
        generalize_venue_category(point.venue_category),
        point.latitude,
        point.longitude,
        point.utc_timestamp,
        point.duration)


def generalize_venue_category(venue_category: str) -> PoiCategory:
    if any(sub_str in categoria for sub_str in ['Shop', 'Store', 'Restaurant', 'Bakery', 'Wash', 'Embassy', 'Ramen', 'Diner', 'Salon', 'Place', 'Steakhouse', 'Market', 'Joint', 'store', 'Food', 'Service', 'Bar', 'Café', 'Cafe', 'Office', 'Bank', 'Mall', 'Newsstand', 'Fair', 'Tea', 'City', 'Gastropub', 'Studio', 'Bodega', 'Rental', 'Dealership', 'Photography Lab', 'Medical Center']):
        return PoiCategory.Business
    elif any(sub_str in categoria for sub_str in ['Factory', 'Military', 'Distillery', 'Government', 'Harbor', 'Facility', 'Winery', 'Brewery']):
        return PoiCategory.Industry
    elif any(sub_str in categoria for sub_str in ['Residential Building', 'Building', 'Shelter', 'Neighborhood', 'Home', 'Hotel', 'Housing', 'House']):
        return PoiCategory.Residence
    elif any(sub_str in categoria for sub_str in ['Scenery', 'Scenic', 'Park', 'Outdoors', 'Garden', 'Museum', 'Castle', 'River', 'Cemetery', 'Temple', 'Synagogue', 'Church', 'Shrine', 'Historic', 'Mosque', 'Planetarium', 'Spot', 'Rest Area', 'Plaza', 'Spiritual', 'Campground']):
        return PoiCategory.Scenery
    elif any(sub_str in categoria for sub_str in ['School', 'College', 'Student', 'University']):
        return PoiCategory.Education
    elif any(sub_str in categoria for sub_str in ['Music', 'Movie', 'Playground', 'Arcade', 'Art', 'Entertainment', 'Gym', 'Nightlife', 'Spa', 'Pool', 'Library', 'Aquarium', 'Beach', 'Zoo', 'Bowling', 'Theater', 'Athletic', 'Casino', 'Comedy', 'Stadium', 'Concert', 'Convention', 'Ski', 'Racetrack']):
        return PoiCategory.Entertainment
    elif any(sub_str in categoria for sub_str in ['Train', 'Bike', 'Airport', 'Ferry', 'Station', 'Road', 'Moving', 'Transport', 'Subway', 'Bridge', 'Travel', 'Taxi', 'Light Rail']):
        return PoiCategory.Transport


def create_similarity_matrix(trajectories: list[TuTrajectory]):
    matrix = []
    for i, trajectory_one in enumerate(trajectories):
        lista = []

        for j in range(i):
            lista.append(matrix[j][i])

        for j, trajectory_two in enumerate(trajectories[i:]):
            if trajectory_one == trajectory_two:
                lista.append(float('-inf'))
            else:
                lista.append(similarity.msm(trajectory_one,trajectory_two))
        matrix.append(lista)
    return matrix



if __name__ == "__main__":
    # lista_categorias = ['College Stadium', 'Sorority House', 'Train Station', 'Mosque', 'Music Venue', 'Nail Salon', 'Subway', 'Internet Cafe', 'Moving Target', 'Residential Building (Apartment / Condo)', 'Bar', 'Mac & Cheese Joint', 'Athletic & Sport', 'Gastropub', 'Building', 'Factory', 'Convention Center', 'Scenic Lookout', 'Professional & Other Places', 'Indian Restaurant', 'Bike Shop', 'Castle', 'Housing Development', 'Mexican Restaurant', 'Event Space', 'Deli / Bodega', 'Casino', 'Beer Garden', 'Church', 'General Travel', 'Ethiopian Restaurant', 'Cosmetics Shop', 'Peruvian Restaurant', 'River', 'Music School', 'School', 'Malaysian Restaurant', 'Comedy Club', 'Road', 'Car Dealership', 'Garden Center', 'Burrito Place', 'South American Restaurant', 'Camera Store', 'Post Office', 'Synagogue', 'Elementary School', 'Law School', 'Latin American Restaurant', 'Bridge', 'Convenience Store', 'Tea Room', 'Rest Area', 'Food Truck', 'Recycling Facility', 'Nursery School', 'Bank', 'Travel Lounge', 'Rental Car Location', 'Animal Shelter', 'College Academic Building', 'Taxi', 'Fair', 'Sculpture Garden', 'Government Building', 'Trade School', 'Harbor / Marina', 'Seafood Restaurant', 'Spanish Restaurant', 'Fraternity House', 'Moroccan Restaurant', 'Historic Site', 'Cajun / Creole Restaurant', 'Temple', 'Miscellaneous Shop', 'Eastern European Restaurant', 'Japanese Restaurant', 'Embassy / Consulate', 'Automotive Shop', 'Funeral Home', 'BBQ Joint', 'Fried Chicken Joint', 'Fish & Chips Shop', 'Italian Restaurant', 'American Restaurant', 'Distillery', 'Australian Restaurant', 'University', 'Flower Shop', 'Food', 'Toy / Game Store', 'Other Great Outdoors', 'Swiss Restaurant', 'Clothing Store', 'Sporting Goods Shop', 'Gaming Cafe', 'Campground', 'Food & Drink Shop', 'Shrine', 'Stadium', 'College & University', 'Spiritual Center', 'Bagel Shop', 'Brazilian Restaurant', 'Cemetery', 'Falafel Restaurant', 'Parking', 'Gift Shop', 'Asian Restaurant', 'Record Shop', 'Bookstore', 'Garden', 'Performing Arts Venue', 'Racetrack', 'Gym / Fitness Center', 'Bakery', 'Museum', 'Diner', 'Design Studio', 'Travel & Transport', 'Laundry Service', 'Sushi Restaurant', 'Hotel', 'Vegetarian / Vegan Restaurant', 'Arts & Crafts Store', 'Hobby Shop', 'Antique Shop', 'German Restaurant', 'Plaza', 'Hot Dog Joint', 'Middle School', 'African Restaurant', 'General College & University', 'Community College', 'Gas Station / Garage', 'Spa / Massage', 'Southern / Soul Food Restaurant', 'Afghan Restaurant', 'Pool', 'Video Store', 'Vietnamese Restaurant', 'Taco Place', 'Mobile Phone Shop', 'Donut Shop', 'College Theater', 'Scandinavian Restaurant', 'Chinese Restaurant', 'Tanning Salon', 'Art Museum', 'Pizza Place', 'Video Game Store', 'Pet Service', 'Fast Food Restaurant', 'Theater', 'Military Base', 'City', 'Drugstore / Pharmacy', 'Sandwich Place', 'Science Museum', 'Ramen /  Noodle House', 'Outdoors & Recreation', 'Caribbean Restaurant', 'Restaurant', 'Bowling Alley', 'Student Center', 'Light Rail', 'Bridal Shop', 'Gluten-free Restaurant', 'General Entertainment', 'Dumpling Restaurant', 'Newsstand', 'Breakfast Spot', 'Wings Joint', 'Candy Store', 'Furniture / Home Store', 'Cupcake Shop', 'Shop & Service', 'Photography Lab', 'Smoke Shop', 'Soup Place', 'Salon / Barbershop', 'Paper / Office Supplies Store', 'Brewery', 'Bike Rental / Bike Share', 'Library', 'Office', 'Motorcycle Shop', 'Bus Station', 'Department Store', 'Neighborhood', 'Mall', 'Burger Joint', 'Electronics Store', 'Ski Area', 'Steakhouse', 'Thai Restaurant', 'Café', 'Korean Restaurant', 'Public Art', 'Medical School', 'Ferry', 'Airport', 'Thrift / Vintage Store', 'Storage Facility', 'Flea Market', 'History Museum', 'Tapas Restaurant', 'Park', 'Salad Place', 'Snack Place', 'Home (private)', 'Planetarium', 'Winery', 'Playground', 'Movie Theater', 'Arcade', 'Dim Sum Restaurant', 'Portuguese Restaurant', 'Nightlife Spot', 'Arts & Entertainment', 'Art Gallery', 'Market', 'Aquarium', 'Concert Hall', 'Beach', 'Coffee Shop', 'Other Nightlife', 'Medical Center', 'Zoo', 'Car Wash', 'Ice Cream Shop', 'Financial or Legal Service', 'Cuban Restaurant', 'High School', 'Pool Hall']
    count = 0
    # for categoria in lista_categorias:
    #     a = generalize_venue_category(categoria)
    #     if a == 'a':
    #         count += 1

    print(count)
    # trajectories = process_trajectories('resources/dataset_TSMC2014_TKY.csv')
    # get_venue_category(trajectories)
    # print(trajectories)