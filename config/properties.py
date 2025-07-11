from pyModelChecking.CTL import AG, AX, EX, Not, Or

enqueue = "enqueue"
dequeue = "dequeue"

# CTL Properties:
# AG(¬dequeue ∨ AX(¬dequeue))
# AG(¬enqueue ∨ EX(dequeue))
properties = {
    "safety": [
        # "never two dequeues in a row"
        ("NoDoubleDequeue",
         AG( Or( Not(dequeue),
                 AX( Not(dequeue) )
              )
         )
        ),
    ],
    "liveness": [
        # "every enqueue can be followed by some dequeue"
        ("EnqueueLeadsToDequeue",
         AG( Or( Not(enqueue),
                 EX(dequeue)
              )
         )
        ),
    ]
}
