# gchq-card
GCHQ Christmas Card Puzzle

It's obviously a QR code, you can tell by the 7's creating the boxes in the top right, bottom left etc. From the size of the Grid it's a Version 2 25x25 QR code.

"input.txt" is the raw puzzle input, "human" is with the intuitave parts of a QR manually annotated to save the solver some time. The 3x QR registation symbols are added, as well as the minimum keepout and the alternating stripes between registrations. On a code of this size there are no additionall tracking boxes.

Solver fills in candidate solutions until the totals sum correctly, using inference from all the remaining candidates to pencil in values. No backtracking was necessary.

It eventually prints:


        $ python score.py
        ...
        ...
         *** Solved ***
        ####### ###   # # #######
        #     # ## ##     #     #
        # ### #     ### # # ### #
        # ### # #  ###### # ### #
        # ### #  ##### ## # ### #
        #     #  ##       #     #
        ####### # # # # # #######
                ###   ###
        # ## ###  # # ### #  # ##
        # #      ### ##    #   #
         #### # #### ## #    ##
         # #   #   # # #### # ###
          ##  # # #      ## #####
           ### ## ## ###### ### #
        # ######### # #  ##    #
         ## #  ##   ## ###     #
        ### # # #  #    ##### #
                #   ## ##   #####
        ####### #  ##   # # # ###
        #     # ##  #  ##   ## #
        # ### #   ####  #####  #
        # ### # ### ########## ##
        # ### # #  ###### ######
        #     #  ##      # # ##
        ####### ##   # ##   #####


From:
![Puzzle source](/puzzle_colorcorrected.jpeg)


score_optim adds a few optimisations to the solver but is more complex.


    chris ~/repos/gchq-card $ time python score.py > /dev/null

    real	0m20.386s
    user	0m20.403s
    sys	0m0.013s
    chris ~/repos/gchq-card $ time python score_optim.py > /dev/null

    real	0m8.229s
    user	0m8.231s
    sys	0m0.010s

