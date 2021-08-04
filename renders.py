from PIL import Image, ImageEnhance

def old_to_new_skin(image):
    final_image = Image.new('RGBA', (64, 64))
    leg_copy = image.crop((0, 16, 16, 32))
    arm_copy = image.crop((40, 16, 56, 32))
    final_image.paste(image, (0, 0))
    final_image.paste(leg_copy, (16, 48))
    final_image.paste(arm_copy, (32, 48))
    return final_image

def skin_to_profile(image, slim):

    final_image = Image.new('RGBA', (12, 12))

    head = face_from_skin(image, (8, 8, 16, 16), (40, 8, 48, 16))
    final_image.paste(head, (2, 2))

    return final_image

def skin_to_portrait(image, slim):

    final_image = Image.new('RGBA', (24, 24))

    head_front = face_from_skin(image, (8, 8, 16, 16), (40, 8, 48, 16))
    final_image.paste(head_front, (10, 2))
    head_side = side_from_skin(image, (0, 8, 8, 16), (32, 8, 40, 16))
    final_image.paste(head_side, (5, 1), head_side)
    body_mid = face_from_skin(image, (20, 20, 28, 32), (20, 36, 28, 48))
    final_image.paste(body_mid, (9, 11))
    if slim:
        arm_left = face_from_skin(image, (36, 52, 39, 64), (52, 52, 55, 64))
    else:
        arm_left = face_from_skin(image, (36, 52, 40, 64), (52, 52, 56, 64))
    final_image.paste(arm_left, (18, 11))
    if slim:
        arm_right = face_from_skin(image, (44, 20, 47, 32), (44, 36, 47, 48))
        final_image.paste(arm_right, (5, 11))
        arm_right_side = side_from_skin(image, (40, 20, 44, 32), (40, 36, 44, 48))
        final_image.paste(arm_right_side, (2, 10), arm_right_side)
    else:
        arm_right = face_from_skin(image, (44, 20, 48, 32), (44, 36, 48, 48))
        final_image.paste(arm_right, (4, 11))
        arm_right_side = side_from_skin(image, (40, 20, 44, 32), (40, 36, 44, 48))
        final_image.paste(arm_right_side, (1, 10), arm_right_side)

    outline_image = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    outline_image.paste(final_image, (-1, 0), final_image)
    outline_image.paste(final_image, (0, -1), final_image)
    outline_image.paste(final_image, (1, 0), final_image)
    outline_image.paste(final_image, (0, 1), final_image)
    enhancer = ImageEnhance.Brightness(outline_image)
    enhanced_im = enhancer.enhance(0.25)
    enhanced_im.paste(final_image, (0, 0), final_image)
    bar = Image.new('RGBA', (24, 1), (0, 0, 0, 0))
    enhanced_im.paste(bar, (0, 23))

    return enhanced_im

def side_from_skin(image, main_pos, overlay_pos):

    main = image.crop(main_pos).convert("RGBA")
    overlay = image.crop(overlay_pos).convert("RGBA")
    
    main_p = Image.new('RGBA', (main.width+2, main.height+2), (0, 0, 0, 0))
    main_p.paste(main, (1, 1))
    
    main_p.paste(overlay, (2, 1), overlay)
    main_p.paste(overlay, (0, 1), overlay)
    
    enhancer = ImageEnhance.Brightness(main_p)
    enhanced_im = enhancer.enhance(0.75)
    
    return enhanced_im.resize(( int(main_p.width/2)+1, main_p.height ), Image.NEAREST)

def face_from_skin(image, main_pos, overlay_pos):

    main = image.crop(main_pos).convert("RGBA")
    overlay = image.crop(overlay_pos).convert("RGBA")
    
    main = Image.alpha_composite(main, overlay)

    return main