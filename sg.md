[Sacred Geometry](http://www.d20pfsrd.com/feats/general-feats/sacred-geometry) is a feat that's stirred up a lot of discussion and derision around here. Nobody seems to like it much: it's confusing, it's OP, it eats up way too much table time and completely ruins pacing, it favors people who've memorized a lot of arithmetical tricks, and calculating the probabilities with it is a royal pain.

So there are two points to this post:
1. Write a script that can find every possible solution, given a level and a dice roll
2. Find out how likely it'll be to find a solution for any given spell and engineering level

First things first: the solver script can be found [here.](https://github.com/trambelus/sandbox/blob/master/sg.py) Python 3.2 or greater is required.

[Here's an example of it in action,](http://i.imgur.com/54Ys2pI.png) and [here](http://i.imgur.com/MUrpasF.png) are some more use cases.

As you can see, it uses a lot of parentheses. There are a lot of [apps](http://sd.af/geo/) [already](https://play.google.com/store/apps/details?id=com.clucasprojects.sacredgeometry) that can solve this, but they don't seem to use parentheses. [Take a look.](http://i.imgur.com/ZpA68Ji.png) Same numbers as above, but it didn't find even one of the twenty possible answers.

Now on to probabilities. Let's assume every player at the table has access to this script, and so if there is a solution, they're guaranteed to find it. Now the question is, if they have four ranks in engineering and are shooting for spell level 6, how likely are they to get a dice roll that works?

I found someone who'd already made a [table for this,](https://i.imgur.com/VglJXiQ.png) ([source](http://www.giantitp.com/forums/showsinglepost.php?p=17841832&postcount=51)) but since that script didn't support parentheses, it undershot on most of those probabilities. It undershot hard.

There's no easy way to cleanly calculate this, so I just [did it the long way.](https://github.com/trambelus/sandbox/blob/master/sgm.py) I set it to randomly roll dice and calculate the results and left it running for ten hours or so, and by the end it had calculated almost fifteen thousand rolls.

[Here are the results.](http://i.imgur.com/ZCv6Ea2.png) Each number is the percent chance that a random dice roll will be successful.

What about [Calculating Mind?](http://www.d20pfsrd.com/feats/general-feats/calculating-mind) What if we're using d8s instead of d6s? Turns out the results are a [lot less interesting.](http://i.imgur.com/WsxWwSU.png) You're more or less guaranteed to get what you want.

Anyway, I hope this sheds some light on one of the most complicated feats in Pathfinder. If anyone wants, I can try to port this to JavaScript and make a browser version, but without multithreading, it'll probably be pretty slow, especially for six or more dice.

I shared this with /u/SeatieBelt and we had a nice little discussion on it, and here are some discussion points he came up with.

* How do you feel about this now? Anyone have their thoughts and feelings changed? Would you allow this at your table? With or without the script?

* How would you feel if it were rewritten as a Mythic Ability, perhaps with a flat d100 roll against the above table for success or failure? We were thinking perhaps having 1 always succeed and 100 always fail.

* How about for NPC's? Would you let your players use it if your NPC's were also allowed to make use of it?

* Finally, what are your favorite gamebreaking combos with this feat?