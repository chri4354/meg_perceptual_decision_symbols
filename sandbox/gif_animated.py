# Not really working..
from moviepy.editor import VideoClip
def make_frame(t):
    img = []
    for hemi in range(2):
        scene.set_time(t*100)
        img.append(np.vstack(scene.save_imageset(None, views=views, colorbar=None, col=hemi)))
    img = np.hstack(img)
    img = np.array([zoom(c, 600. / img.shape[1])
            for c in img.transpose((2, 0, 1))]).transpose((1, 2, 0))
    return img

animation = VideoClip(make_frame, duration=6) # 3-second clip

# For the export, many options/formats/optimizations are supported
animation.write_gif("my_animation.gif", fps=15) # export as GIF (slow)
report.add_image_to_section("my_animation.gif", contrast['name'], subject)
