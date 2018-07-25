So far this is in it's first stage. I'll show you a simple script, but this isn't meant to be used quite yet. 
I'm just uploading the very first version I have for my friend to help me work on it.

from Pillow3f.Renderer import RenderPipeline

a, b, c = [-2, 0, 1], [-4, 0, -1], [-3, 12, 0]
shape1 = [a, b, c]
a, b, c = [1, 0, 1], [-1, 0, -1], [0, 1.5, 0]
shape2 = [a, b, c]

Pipe = RenderPipeline(600, 800)
Pipe.camera = [[0, 0, -20], [0, x*(45/5), 0]]
        
Pipe.triangle(shape1, [[150, 75, 0, 255], [150, 75, 0, 255], [0, 75, 200, 255]])    
Pipe.triangle(shape2, [[255, 0, 0, 128], [0, 255, 0, 255], [0, 0, 255, 255]])
        
Pipe.save('png', 'C:/', 'newRendered_image%s' % x)
print(Pipe.angle(*shape1))
print(Pipe.angle(*shape2))

Things you should know before using this: A z-buffer hasn't been implemented yet, 
but I have a plan on how to do so while keeping the whole layout the same. 
It will be jerry-rigged, but, the results will be the same and alpha will still work. 
And because it will be jerry rigged it will be much faster. 
I really don't want to say how I will do it, but I will. 
The alpha on the pixel will be replaced with the z-value, 
then the z value of that pixel will be compared against an overwriting pixel. 
The overwriting pixel's alpha is used to determine the mix of the colors, 
and then when it's all said and done, 
the whole image is rewritten to have alphas of 255 before it is saved or displayed.
