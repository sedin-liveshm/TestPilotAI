from typing import Annotated, List, Literal, Optional, Union
from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# LOCATOR STRATEGIES (Discriminated union on 'strategy')
# Mirrors automation/src/ir/schema.ts LocatorTargetSchema
# ============================================================================

class RoleLocator(BaseModel):
    strategy: Literal["role"]
    role: str = Field(..., min_length=1)
    name: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class TextLocator(BaseModel):
    strategy: Literal["text"]
    value: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class LabelLocator(BaseModel):
    strategy: Literal["label"]
    value: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class PlaceholderLocator(BaseModel):
    strategy: Literal["placeholder"]
    value: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class TestIdLocator(BaseModel):
    strategy: Literal["testId"]
    value: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class CssLocator(BaseModel):
    strategy: Literal["css"]
    value: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


LocatorTarget = Annotated[
    Union[
        RoleLocator,
        TextLocator,
        LabelLocator,
        PlaceholderLocator,
        TestIdLocator,
        CssLocator,
    ],
    Field(discriminator="strategy"),
]


# ============================================================================
# ACTIONS (Discriminated union on 'type')
# Mirrors automation/src/ir/schema.ts TestActionSchema
# ============================================================================

class NavigateAction(BaseModel):
    type: Literal["navigate"]
    url: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class ClickAction(BaseModel):
    type: Literal["click"]
    target: LocatorTarget

    model_config = ConfigDict(extra="forbid")


class FillAction(BaseModel):
    type: Literal["fill"]
    target: LocatorTarget
    value: str

    model_config = ConfigDict(extra="forbid")


class SelectAction(BaseModel):
    type: Literal["select"]
    target: LocatorTarget
    value: str

    model_config = ConfigDict(extra="forbid")


class CheckAction(BaseModel):
    type: Literal["check"]
    target: LocatorTarget

    model_config = ConfigDict(extra="forbid")


class UncheckAction(BaseModel):
    type: Literal["uncheck"]
    target: LocatorTarget

    model_config = ConfigDict(extra="forbid")


class PressAction(BaseModel):
    type: Literal["press"]
    target: Optional[LocatorTarget] = None
    key: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class WaitAction(BaseModel):
    type: Literal["wait"]
    durationMs: float = Field(..., gt=0)

    model_config = ConfigDict(extra="forbid")


class AssertTextAction(BaseModel):
    type: Literal["assertText"]
    target: LocatorTarget
    text: str

    model_config = ConfigDict(extra="forbid")


class AssertVisibleAction(BaseModel):
    type: Literal["assertVisible"]
    target: LocatorTarget

    model_config = ConfigDict(extra="forbid")


class AssertUrlAction(BaseModel):
    type: Literal["assertUrl"]
    url: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class ScreenshotAction(BaseModel):
    type: Literal["screenshot"]
    name: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


TestAction = Annotated[
    Union[
        NavigateAction,
        ClickAction,
        FillAction,
        SelectAction,
        CheckAction,
        UncheckAction,
        PressAction,
        WaitAction,
        AssertTextAction,
        AssertVisibleAction,
        AssertUrlAction,
        ScreenshotAction,
    ],
    Field(discriminator="type"),
]


# ============================================================================
# CANONICAL TEST IR SCHEMA (v1)
# Mirrors automation/src/ir/schema.ts TestIRSchema
# ============================================================================

class TestIR(BaseModel):
    version: Literal["1"]
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    actions: List[TestAction] = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")
