My Philosopy on Driving
#########################

.. note::

   I think this is a `hypocrite commit`_ I have copied from `my blog article on driving`_. I use this blog article to demonstrate LaTeX_ formulae in Sphinx_ documentation for a presentation I (Tanim Islam) will give on 5 AUGUST 2021. I will present on using Sphinx_ documentation to the Sacramento Python Users' Group on that day.

This consists of notes, that I fleshed out (with animations! with pictures!) of my driving philosophy.

**REAL TITLE**: "Off the highway, and out of the country, you should be driving 5-10 miles per hour under the speed limit".

As you all may know, a bunch of lazy justifications and illogical and kind of circular rules turn this philosophy, or mission statement, into a religion. The only thing it's missing are followers and an official bible.

Lots of people who aren't paying attention (like yourself), and lots of traffic lights randomly turn red and stay that way.

Why hurry up and wait -- the red light isn't getting any greener? And why give yourself less time to anticipate accidents? Why ruin your car's brakes or waste energy (if you don't have a hybrid or electric)? Why stress yourself at all?

Here's a few things that work great for me.

* Cruise 5 MPH below the speed limit in normal traffic, aim for 10 MPH during rush hour.

* In a traffic jam, say the car in front of you is stopping and going; wait 10 seconds before it starts moving, and just take your foot off the brakes. Coast! Don't put on the gas until traffic starts moving 20 MPH or faster for 30 seconds or longer.

* If the light in front of you turns red, take your foot off the gas.

* If you're going to turn into another road, right or left, coast (even with a green light) so that you roll into the street at 15 MPH. 15 MPH is the fastest you can take turns without wearing your tires.

What about hills? I'm talking about this some more since this is the newest chapter in my bible.

* Going up hills are an opportunity for gravity to do your work for you (so to speak): light's red, you're going up, so cruise slower and coast earlier. Time your speed and your FOOT OFF THE PEDAL so you roll to a stop at the red light. Bonus points if you're going 10 MPH when the light goes green.

* If you're going up a hill, tap your brakes 5 feet vertically from the top and coast through. Aim to go 5 MPH below the speed limit at the bottom of the hill.

* If there's a red light at the bottom of the hill, just put your feet on the brakes so you slow constantly to a stop at the light.
  
* If it's green and you're taking a turn, slow constantly so that you're going 15 MPH through it.

Make it fun and habit forming for you! ( Slow driving is just curling! )

* The lights in front are probably going to turn red soon, if they're green. Why rush by putting your foot on the gas? Just coast if you feel it.

* See how close you can get to the red light before it turns green, or try to get to the red light JUST as it turns green.

* Let gravity and friction do the work for you!

And before you just say no, see if you can answer this: you're trying this out, some driver goes in front of you, and there's that red light. If they end up the same place you did, except they hurried to get there, why not keep on keeping on? Or at least until you get shot.

THE MATH
^^^^^^^^^^
These notes come from the 10-minute-long Washington Society literary presentation I gave on 24 April 2020, colloquially titled, "Off the highway, you should drive 5-10 MPH below the speed limit."

One of the main points in my talk was that you should aim for speeds of about 13 MPH when turning left or right onto a road at 90 degrees from yours, in order to get the maximum acceleration that will keep your tires from wear. I soon realized that the turning radius is approximately 30 feet. If we round up to 15 MPH [1]_, then the acceleration here is,

.. _eq-canonical-accels:

.. math::

   a_{\text{canonical}} = \frac{ v_0^2}{r_0} \approx 4.92\text{ m/s$^2$} \approx 0.5\text{ g}.

Here, :math:`v_0 = 15\text{ mph} \approx 6.71\text{ m/s}`, and :math:`r_0 = 30\text{ ft} \approx 9.1\text{ m}`. One can then make this canonical acceleration and deceleration when controlling your car: acceleration from stop, deceleration to stop sign or turning road, and so on.

I want to explore accelerating from rest, into a 90 degree turn, over the 30 foot turning radius, such that the total acceleration stays at :math:`a_0`. Geometry is below in `problem depiction <fig-turn-cartoon_>`_,

.. _fig-turn-cartoon:

.. figure:: https://tanimislam.gitlab.io/blog/2020/09/driving/turn_cartoon.png
   :width: 100%
   :align: left

   Cartoon showing the geometry of the car’s motion along the circle from a stop, through a turn of radius :math:`r_0`, and a constant
   total acceleration of :math:`a_0`.

Since the car starts from rest, at :math:`\theta = 0`, the angular velocity :math:`\dot{\theta} = 0`.

The canonical equation of acceleration is,

.. _eq-canonical-accel-relation:

.. math:: r_0\sqrt{\ddot{\theta}^2 + \dot{\theta}^4} = v_0^2 / r_0.
	   
If we make the following variable changes,

.. _eq-time-scaling:

.. math:: \tau = \frac{v_0 t}{r_0},

.. _eq-norm-angular-velocity:
	  
.. math:: \dot{\theta} = \frac{v_0}{r_0} y,

.. _eq-norm-angular-accel:

.. math:: \ddot{\theta} = \left(\frac{v_0}{r_0}\right)^2 \left(\frac{dy}{d\tau}\right).

Then the `canonical acceleration relation <eq-canonical-accel-relation_>`_ reduces to,

.. _eq-master-relation:

.. math:: \left( \frac{dy}{d\tau} \right)^2 + y^4 = 1.

with the condition that :math:`y(0) = 0`.

Note that :math:`y = v/v_0`, where :math:`v` is the car speed; and the normalized transverse acceleration :math:`a_{\text{trans}}` is,

.. _eq-trans-acceleration:

.. math:: a_{\text{trans}} = \left( \frac{dy}{d\tau} \right) \frac{v_0^2}{r_0} = \frac{v_0^2}{r_0}\left( 1 - \frac{v^4}{v_0^4} \right).

The solution to the `the master relation <eq-master-relation_>`_ comes from `Wolfram Alpha`_,

.. _eq-relation-between-y-and-tau:

.. math:: y\times \mbox{}_2F_1\left( \frac{1}{4},\frac{1}{2}; \frac{5}{4}, y^4 \right) = \tau.

The angle that is traversed as a function of time is,

.. _eq-theta-unsimplified:

.. math:: \theta(t) = \int_0^t \dot{\theta}\left( t' \right)\,dt' = \int_0^{\tau}\frac{v_0}{r_0} y\left( \tau' \right) \frac{r_0}{v_0}\,d\tau' = \int_0^{\tau} y \left( \tau' \right)\,d\tau'.

After more `Wolfram Alpha`_, one can then show that the angle is related to the scaled speed :math:`y = v/v_0` by this relation,

.. _eq-theta-relation:

.. math:: \sin\theta = \frac{v^2}{2 v_0^2}.

The speed :math:`v` versus scaled time :math:`\tau` is shown in `this illustrative figure <fig-turn-speed-accel_>`_.

.. _fig-turn-speed-accel:

.. figure:: https://tanimislam.gitlab.io/blog/2020/09/driving/turn_speed_accel.png
   :width: 100%
   :align: left
   
   On the left is scaled speed versus scaled time, and on the right is scaled *transverse* acceleration versus scaled time.

The angle, in degrees, along its motion as a function of time is shown in `another illustrative figure <fig-turn-angle_>`_.

.. _fig-turn-angle:

.. figure:: https://tanimislam.gitlab.io/blog/2020/09/driving/turn_angle.png
   :width: 100%
   :align: left
	    
   Position, in degrees, along the curve as a function of scaled time, :math:`\approx 1.311` (see `the relation on scaled maximum time <eq-tmax_>`_).

Here are the properties of this car’s motion, in general and specific to my definition of "safe driving" (constant speed of 15 MPH through a 30 FT turning radius).

* Its maximum speed, :math:`v_{\text{max}} = v_0`; in my case, 15 MPH.

* It reaches its maximum speed at :math:`t_{\text{max}}`, given by,

  .. _eq-tmax:
  
  .. math:: t_{\text{max}} = \frac{\sqrt{\pi} \Gamma( 5/4 )}{\Gamma( 3/4 )} r_0 / v_0 \approx 1.311 r_0 / v_0.

  In my case, this is approximately 1 second later.

* It reaches this maximum speed at an angle of 30 degrees along its motion, :math:`\theta_{\text{max}} = \pi/6`, see the `theta relation <eq-theta-relation_>`_, or in my case approximately 16 feet into the circle.

* In my case, start accelerating at 0.5 g, or when looking at the speedometer, a change in speed of :math:`\approx 11` MPH/second.

I continue to move at a speed :math:`v_0` along that circle for 90 degrees, until moving into the perpendicular street.

.. [1] I move at 15 MPH because it is easier to gauge this speed on my odometer.
.. _`Wolfram Alpha`: https://www.wolframalpha.com
.. _`hypocrite commit`: https://lore.kernel.org/lkml/202105051005.49BFABCE@keescook
.. _`my blog article on driving`: https://tanimislam.gitlab.io/blog/my-philosophy-on-driving.html
.. _LaTeX: https://www.latex-project.org
.. _Sphinx: https://www.sphinx-doc.org/en/master
