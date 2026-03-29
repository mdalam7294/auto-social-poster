@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        idea = request.form['idea']
        style = request.form.get('style', 'cinematic')
        duration = int(request.form.get('duration', 60))
        
        # Generate faceless video
        video_path, scenes = generate_faceless_video(idea, style, duration)
        
        # SEO metadata
        title = f"AI Generated: {idea[:60]}"
        description = f"An AI-generated video about {idea}. Created automatically with AI visuals and voice."
        tags = ["ai", "faceless", idea.lower().replace(" ", "")]
        title, description, tags = generate_high_rpm_seo(title, description, tags)
        
        metadata = {
            'title': title,
            'description': description,
            'tags': tags,
            'privacy': 'public'
        }
        
        # Schedule upload
        result = schedule_upload(upload_youtube_video, video_path, metadata, current_user)
        return render_template('result.html', result=result)
    
    return render_template('create.html')
