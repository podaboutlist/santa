# Santa bot Design Doc

## Table of Contents

1. [Overview](#1-overview)
2. [Gameplay Loop](#2-gameplay-loop)
   1. [Gameplay Loop A](#a-loop-a)
   2. [Gameplay Loop B](#b-loop-b)
3. [Functionality](#3-functionality)
4. [Database Design](#4-database-design)
   1. [users](#a-users)
   2. [presents](#b-presents)
5. [Tech Stack](#5-tech-stack)
6. [Project Style Guides](#6-Project-Style-Guides)
   1. [Code Style](#a-code-style)
   2. [Committing](#b-Committing)

## 1. Overview

Santa bot provides a basic game that functions around users asking for presents.
The goal for the User is to acquire as many presents as possible. Gathering
more presents increases the chances of the Grinch visiting the User when they
request a present, stealing all of the User's presents. The User has several
options during gameplay to decrease their odds of receiving a vist from the
Grinch.

At 11:59 PM EST on 24 December 2020, the game will lock, not allowing any more
gameplay input from users. They will retain the ability to view the total amount
and details of presents owned by themselves and other players. The player with
the most presents is declared the "Winner of Christmas." No further interaction
or sustained gameplay is planned to take place after this happens.


## 2. Gameplay Loop

### A. Loop A

A User asks Santa for a present. **One** of these three events happen.

   1. Santa gives the User a present. The User's Present Count (PC) is
      incremented by one.
      - If the User said "please" when asking for a present, there is a
         chance Santa will give them **two** presents. One that the User
         asked for, and one picked randomly from the names of existing
         presents or a pre-defined list.
   2. The Grinch visits the User, stealing all of their presents. The User's
      Present Count is reset to zero.
      - If the User said "please" when asking for a present, there is a
         chance Santa will fight the Grinch. The User neither gains nor loses
         presents if this happens.
   3. The User receives a time-based cooldown which must expire before they
      can ask for another present.
      - If the User asks for a present without saying "please" during this
         cooldown, the timer is reset to its original duration and the User
         is notified.
      - If the User says "please" when asking for a present during their
         cooldown, they are notified of the remaining time in the cooldown but
           suffer no ill effects.

### B. Loop B

A User asks Santa to give another User (Doug) a present. **All** of these events
happen:

   1. Santa gives Doug a present. There is zero chance of either the Grinch
      appearing or the gifting of double presents.
   2. The User receives a 24 hour cooldown before they can give a gift to
      another user again.
      - If the User attempts to gift to another player during this cooldown,
         no penalty is sustained.


## 3. Functionality

Santa Bot operates through Discord commands. The following commands are
available:
   - `[please] give [@user] <present name>` - Gives a present.
     - `@user` and "please" are optional.
     - If `@user` is specified, Gameplay Loop #2 activates.
     - Otherwise, Gameplay Loop #1 activates.
   - `my info` - Displays statistics for the User.
     - current present count
     - \# of stolen presents
     - \# of presents sent
     - \# of presents received
     - last gift receipt date/time
     - on cooldown?,
   - `my presents` - Displays a list of the User's presents.
     - Ten present names at a time, paginated
     - Pagination implemented with arrow emoji reactions
   - `global info` - Displays global statistics
     - current global present count
     - global # of stolen presents
     - global # of presents sent
     - global # of presents received
     - last gift
       - name
       - receipt date/time
       - sender
       - receiver
     - last User visited by the Grinch
     - last User visited by Santa
   - `global top` - Displays top Users from the leaderboard
     - Ten users at a time, paginated
     - Pagination implemented with arrow emoji reactions
     - Statistics shown for each user
       - current present count
       - \# of stolen presents
       - \# of presents sent
       - \# of presents received
   - `help` - Displays command usage
     - Either a link to a website with command usage (i.e. GitHub Wikis), or a
       list of commands and their options
   - `invite` - Prints a message that the Bot is self-hosted with link to GitHub
     repo.


## 4. Database Design

**NB:** I am a novice database designer. Consider this section a work in
progress and subject to change.

The following objects need to have their data preserved in a database with the
listed attributes:

### A. `users`
   - `id` (`BIGINT PRIMARY KEY`) - derived from the User's Discord ID
   - `presents` - one-to-many relationship between the User and their presents
   - `total_presents` (`INTEGER >= 0`) - cached number of presents the User
     currently possesses
   - `stolen_presents` (`INTEGER`) - the number of presents the User has lost
     to the Grinch
   - `given_presents` (`INTEGER >= 0`) - cached number of presents the user has
     given
   - `total_snatches` (`INTEGER >= 0`) - number of times the Grinch has stolen
     presents from the User
   - `last_gift` (`TIMESTAMP`) - the last time the User was given a gift

### B. `presents`
   - `id` (`INTEGER PRIMARY KEY`)
   - `name` (`TEXT`) - the name of the present
   - `owner` (`FOREIGN KEY(users) NOT NULL`) - the User who owns the present
   - `gifter` (`FOREIGN KEY(users)`) - the User who gifted the present (optional)
     - If `gifter` is `null` we attribute the gift to Santa.
   - `stolen` (`BOOLEAN NOT NULL`) - if the present was stolen by the Grinch
   - `date_received` (`TIMESTAMP NOT NULL`) - when the present was given

### C. `servers`
   - `id` (`BIGINT PRIMARY KEY`) - server's ID from Discord
   - `webhook` (`TEXT`) - Grinch Webhook URL for the server


## 5. Tech Stack

The Santa project currently uses the following tech:

   - Python 3
     - [Discord.py][1] for Discord integration
     - [Pony ORM][2] for database interaction
   - PostgreSQL as the database backend


## 6. Project Style Guides

### A. Code Style

All code must pass `pycodestyle` checks. A future commit will enable CI to
automatically check this.

### B. Committing

See [@Angular/CONTRIBUTING.md#commit][3]. There are no limitations to options
for "type" and "scope" in this project, but please keep the general format
of the commit messages specified above.


[1]: https://discordpy.readthedocs.io/en/latest/index.html
[2]: https://docs.ponyorm.org/
[3]: https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit
