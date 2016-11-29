#!/usr/bin/env python

import pandas as pd
import numpy as np
from wordcloud import WordCloud
from PIL import Image
import itertools as it

def grey_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 0%%, %d%%)" % random.randint(0, 30)

def blue_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(240, 70%%, %d%%)" % random.randint(20, 40)

def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    return "hsl(0, 70%%, %d%%)" % random.randint(20, 40)

def get_words_and_frequencies(neurosynth_file, pos=True):

    df = pd.read_csv(neurosynth_file)
    df = df.dropna(axis=1)

    # Only keep the top 100 (or bottom 100) observations
    if pos:
        df = df.iloc[:100, :]
    else:
        df = df.iloc[(-100):, :]
        df['corr.'] = df['corr.']*-1.0

    # multiply the correlations by 100 to give you more reasonable numbers
    df['corr.'] = df['corr.']*100

    return df

def create_word_cloud(df, mask_file, font_path):

    mask = np.array(Image.open(mask_file))

    wc = WordCloud(relative_scaling=0.5,
                        mask=mask,
                        prefer_horizontal=1.0,
                        background_color='white',
                        font_path=font_path)

    wc.generate_from_frequencies(df.values)

    return wc

def plot_word_cloud(neurosynth_file, wc, pos=True, grey=False):

    # Create the figure
    fig, ax = plt.subplots(figsize=(10,10))

    # Get the right color function
    color_func = grey_color_func
    if not grey:
        if pos:
            color_func = red_color_func
        else:
            color_func = blue_color_func

    # Show the word cloud
    plt.imshow(wc.recolor(color_func=color_func, random_state=3))

    # Get rid of the axes and the white around the outside of the plot
    ax.set_axis_off()
    plt.tight_layout()

    # Figure out the right name for the file
    if pos:
        fig_name = neurosynth_file.replace('.csv', '_pos.png')
    else:
        fig_name = neurosynth_file.replace('.csv', '_neg.png')

    print fig_name
    # Save the figure
    fig.savefig(fig_name, bbox_inches=0)

    plt.close()


#==============================================================================
# HERE WE GO!

mask_file = 'VOLUME_MAPS/circle_mask.png'
font_path = 'VOLUME_MAPS/ufonts.com_gillsans.ttf'

for pls, pos in it.product(range(5), [True, False]):

    neurosynth_file = 'VOLUME_MAPS/PLS_{}_Neurosynth.csv'.format(pls)
    df = get_words_and_frequencies(neurosynth_file, pos=pos)

    wc = create_word_cloud(df, mask_file, font_path)

    plot_word_cloud(neurosynth_file, wc, pos=pos)
