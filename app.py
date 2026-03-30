@app.route('/channels')
@login_required
def channels():
    return render_template('channels.html', channels=current_user.youtube_channels)

@app.route('/connect/youtube')
@login_required
def connect_youtube():
    auth_url = youtube_auth_url()
    return redirect(auth_url)

@app.route('/youtube/callback')
@login_required
def youtube_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if code and state and youtube_callback_handler(code, state):
        flash('YouTube channel added successfully!')
    else:
        flash('Failed to add channel')
    return redirect(url_for('channels'))

@app.route('/remove_channel/<int:channel_id>')
@login_required
def remove_channel(channel_id):
    channel = YouTubeChannel.query.get_or_404(channel_id)
    if channel.user_id != current_user.id:
        flash('Unauthorized')
        return redirect(url_for('channels'))
    db.session.delete(channel)
    db.session.commit()
    flash('Channel removed')
    return redirect(url_for('channels'))
