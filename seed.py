from app import create_app
from models import db, User, Video
from utils import parse_video_url

app = create_app()

def seed_database():
    with app.app_context():
        db.create_all()
        if User.query.first() is not None:
            print("Database already seeded.")
            return

        demo_user = User(username='demo_user', email='demo@streamtube.com')
        demo_user.set_password('password123')
        db.session.add(demo_user)
        db.session.commit()

        sample_videos = [
            {
                'title': 'Big Buck Bunny (Sample)',
                'description': 'A large and lovable rabbit deals with bullying forest creatures.',
                'url': 'https://www.youtube.com/watch?v=aqz-KE-bpKQ',
                'category': 'Entertainment'
            },
            {
                'title': 'Python Tutorial for Beginners',
                'description': 'Learn Python programming in this full course for beginners.',
                'url': 'https://www.youtube.com/watch?v=_uQrJ0TkZlc',
                'category': 'Education'
            },
            {
                'title': 'Chill Lofi Beats to Code/Relax To',
                'description': 'Relaxing lofi hip hop radio beats to study and code to.',
                'url': 'https://www.youtube.com/watch?v=jfKfPfyJRdk',
                'category': 'Music'
            },
            {
                'title': 'Trendy Hindi Song - Kesariya (Lyrical)',
                'description': 'Enjoy the latest trendy Bollywood hit song.',
                'url': 'https://www.youtube.com/watch?v=BddP6PYo2gs',
                'category': 'Music'
            },
            {
                'title': 'Minecraft Survival Let\'s Play - Episode 1',
                'description': 'Building our first house and surviving the first night in Minecraft!',
                'url': 'https://www.youtube.com/watch?v=2W4wXQ1R4aE',
                'category': 'Gaming'
            }
        ]

        for v in sample_videos:
            parsed = parse_video_url(v['url'])
            video = Video(
                title=v['title'],
                description=v['description'],
                url=v['url'],
                embed_url=parsed['embed_url'],
                video_type=parsed['type'],
                thumbnail_url=parsed['thumbnail'],
                category=v['category'],
                user_id=demo_user.id
            )
            db.session.add(video)

        db.session.commit()
        print("Database seeded successfully with demo user and videos!")

if __name__ == '__main__':
    seed_database()