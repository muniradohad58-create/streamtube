from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from models import db, Video, Comment, Like, WatchHistory, Watchlist, SearchHistory
from utils import parse_video_url

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/')
def home():
    category = request.args.get('category', 'All')
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Video.query
    if category and category != 'All':
        query = query.filter_by(category=category)

    pagination = query.order_by(Video.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    videos = pagination.items
    
    categories = ['All', 'Music', 'Gaming', 'Tech', 'Education', 'Entertainment', 'General']

    return render_template('videos/home.html', videos=videos, pagination=pagination, categories=categories, selected_category=category)

@videos_bp.route('/video/<int:video_id>', methods=['GET', 'POST'])
def watch(video_id):
    video = Video.query.get_or_404(video_id)

    if current_user.is_authenticated:
        history = WatchHistory(user_id=current_user.id, video_id=video.id)
        db.session.add(history)
        db.session.commit()

    if request.method == 'POST' and current_user.is_authenticated:
        content = request.form.get('content')
        if content:
            comment = Comment(content=content, user_id=current_user.id, video_id=video.id)
            db.session.add(comment)
            db.session.commit()
            flash('Comment added!', 'success')
        return redirect(url_for('videos.watch', video_id=video.id))

    related_videos = Video.query.filter(Video.category == video.category, Video.id != video.id).limit(6).all()
    if not related_videos:
        related_videos = Video.query.filter(Video.id != video.id).limit(6).all()

    likes_count = Like.query.filter_by(video_id=video.id, is_like=True).count()
    dislikes_count = Like.query.filter_by(video_id=video.id, is_like=False).count()
    user_like = None
    in_watchlist = False

    if current_user.is_authenticated:
        ul = Like.query.filter_by(video_id=video.id, user_id=current_user.id).first()
        if ul:
            user_like = ul.is_like
        in_watchlist = Watchlist.query.filter_by(video_id=video.id, user_id=current_user.id).first() is not None

    comments = Comment.query.filter_by(video_id=video.id).order_by(Comment.created_at.desc()).all()

    return render_template('videos/watch.html', video=video, related_videos=related_videos, 
                           likes_count=likes_count, dislikes_count=dislikes_count, 
                           user_like=user_like, in_watchlist=in_watchlist, comments=comments)

@videos_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        raw_url = request.form.get('url')
        category = request.form.get('category', 'General')

        if not title or not raw_url:
            flash('Title and URL are required.', 'danger')
            return redirect(url_for('videos.upload'))

        parsed = parse_video_url(raw_url)

        video = Video(
            title=title,
            description=description,
            url=raw_url,
            embed_url=parsed['embed_url'],
            video_type=parsed['type'],
            thumbnail_url=request.form.get('thumbnail_url') or parsed['thumbnail'],
            category=category,
            user_id=current_user.id
        )
        db.session.add(video)
        db.session.commit()
        flash('Video uploaded successfully!', 'success')
        return redirect(url_for('videos.home'))

    return render_template('videos/upload.html')

@videos_bp.route('/video/<int:video_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('videos.home'))

    if request.method == 'POST':
        video.title = request.form.get('title')
        video.description = request.form.get('description')
        video.category = request.form.get('category')
        db.session.commit()
        flash('Video updated successfully!', 'success')
        return redirect(url_for('videos.watch', video_id=video.id))

    return render_template('videos/edit.html', video=video)

@videos_bp.route('/video/<int:video_id>/delete', methods=['POST'])
@login_required
def delete_video(video_id):
    video = Video.query.get_or_404(video_id)
    if video.user_id != current_user.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('videos.home'))

    db.session.delete(video)
    db.session.commit()
    flash('Video deleted.', 'info')
    return redirect(url_for('videos.home'))

@videos_bp.route('/video/<int:video_id>/like/<int:action>', methods=['POST'])
@login_required
def like_video(video_id, action):
    is_like = bool(action)
    existing_like = Like.query.filter_by(video_id=video_id, user_id=current_user.id).first()

    if existing_like:
        if existing_like.is_like == is_like:
            db.session.delete(existing_like)
        else:
            existing_like.is_like = is_like
    else:
        new_like = Like(is_like=is_like, user_id=current_user.id, video_id=video_id)
        db.session.add(new_like)
    
    db.session.commit()
    return redirect(url_for('videos.watch', video_id=video_id))

@videos_bp.route('/watchlist/toggle/<int:video_id>', methods=['POST'])
@login_required
def toggle_watchlist(video_id):
    item = Watchlist.query.filter_by(video_id=video_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        flash('Removed from Watchlist', 'info')
    else:
        newItem = Watchlist(video_id=video_id, user_id=current_user.id)
        db.session.add(newItem)
        flash('Added to Watchlist', 'success')
    db.session.commit()
    return redirect(url_for('videos.watch', video_id=video_id))

@videos_bp.route('/watchlist')
@login_required
def watchlist():
    items = Watchlist.query.filter_by(user_id=current_user.id).order_by(Watchlist.added_at.desc()).all()
    return render_template('videos/watchlist.html', items=items)

@videos_bp.route('/history')
@login_required
def history():
    history_items = WatchHistory.query.filter_by(user_id=current_user.id).order_by(WatchHistory.watched_at.desc()).all()
    return render_template('videos/history.html', history_items=history_items)

@videos_bp.route('/history/clear', methods=['POST'])
@login_required
def clear_history():
    WatchHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Watch history cleared.', 'info')
    return redirect(url_for('videos.history'))

@videos_bp.route('/history/remove/<int:history_id>', methods=['POST'])
@login_required
def remove_history_item(history_id):
    item = WatchHistory.query.get_or_404(history_id)
    if item.user_id == current_user.id:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('videos.history'))

@videos_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    if q and current_user.is_authenticated:
        sh = SearchHistory(query=q, user_id=current_user.id)
        db.session.add(sh)
        db.session.commit()

    videos = []
    if q:
        videos = Video.query.filter(
            (Video.title.ilike(f'%{q}%')) | 
            (Video.description.ilike(f'%{q}%')) | 
            (Video.category.ilike(f'%{q}%'))
        ).all()

    return render_template('videos/search.html', videos=videos, query=q)

@videos_bp.route('/api/search-suggestions')
def search_suggestions():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    
    videos = Video.query.filter(Video.title.ilike(f'%{q}%')).limit(5).all()
    return jsonify([v.title for v in videos])

@videos_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('videos.watch', video_id=comment.video_id))
    
    video_id = comment.video_id
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted', 'info')
    return redirect(url_for('videos.watch', video_id=video_id))