# audioControls.py

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QSlider, QGroupBox
from PyQt6.QtCore import Qt

def buildAudioControls(volSlider, sqlSlider) -> QGroupBox:
    volLayout = QVBoxLayout()
    volLabel = QLabel("Vol")
    volLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    volSlider.setRange(0, 100)
    volSlider.setValue(50)
    volLayout.addWidget(volLabel)
    volLayout.addWidget(volSlider)

    sqlLayout = QVBoxLayout()
    sqlLabel = QLabel("SQL")
    sqlLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sqlSlider.setRange(0, 100)
    sqlSlider.setValue(30)
    sqlLayout.addWidget(sqlLabel)
    sqlLayout.addWidget(sqlSlider)

    slidersLayout = QHBoxLayout()
    slidersLayout.addLayout(volLayout)
    slidersLayout.addLayout(sqlLayout)

    audioGroup = QGroupBox("Audio")
    audioGroup.setLayout(slidersLayout)

    return audioGroup
