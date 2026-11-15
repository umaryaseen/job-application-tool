"""Reviewed internal skill concepts and aliases (TASK-013, ADR-006).

Every alias is an explicit, reviewed equivalence for one concept. Broader and
related links are typed relations only: they never make two concepts the same
(PyTorch is not deep learning; SageMaker is not AWS). No external taxonomy,
model or network source is used. Add entries only with a rationale and review.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import StringConstraints

from ..domain.common import StrictModel

# Concept IDs may be a single letter ("c", "r"), unlike general stable IDs.
ConceptId = Annotated[
    str, StringConstraints(min_length=1, max_length=64, pattern=r"^[a-z][a-z0-9_-]*$")
]

DICTIONARY_VERSION: Literal["skill-aliases-v1"] = "skill-aliases-v1"

AliasStyle = Literal["word", "abbreviation", "letter", "symbol"]
# word: case-insensitive, letter/digit boundaries; abbreviation: case-sensitive
# word; letter: single case-sensitive letter with strict neighbours; symbol:
# case-insensitive, not preceded by a letter, digit or "." nor followed by a
# letter or digit.


class Alias(StrictModel):
    text: str
    style: AliasStyle = "word"
    status: Literal["exact", "ambiguous"] = "exact"


class Relation(StrictModel):
    type: Literal["broader", "related"]
    target: ConceptId


class Concept(StrictModel):
    concept_id: ConceptId
    label: str
    kind: Literal["technology", "language", "field"]
    aliases: tuple[Alias, ...]
    relations: tuple[Relation, ...] = ()
    rationale: str


def _w(*texts: str) -> tuple[Alias, ...]:
    return tuple(Alias(text=text) for text in texts)


def _a(*texts: str) -> tuple[Alias, ...]:
    return tuple(Alias(text=text, style="abbreviation") for text in texts)


def _s(*texts: str) -> tuple[Alias, ...]:
    return tuple(Alias(text=text, style="symbol") for text in texts)


def _broader(target: str) -> tuple[Relation, ...]:
    return (Relation(type="broader", target=target),)


def _related(target: str) -> tuple[Relation, ...]:
    return (Relation(type="related", target=target),)


CONCEPTS: tuple[Concept, ...] = (
    Concept(
        concept_id="c",
        label="C",
        kind="technology",
        aliases=(Alias(text="C", style="letter"),),
        rationale="Single letter; strict neighbours exclude C-level, Objective-C, C++, C#.",
    ),
    Concept(
        concept_id="cpp",
        label="C++",
        kind="technology",
        aliases=_s("C++"),
        rationale="Distinct language from C and C#.",
    ),
    Concept(
        concept_id="csharp",
        label="C#",
        kind="technology",
        aliases=_s("C#"),
        rationale="Distinct language from C and C++.",
    ),
    Concept(
        concept_id="r",
        label="R",
        kind="technology",
        aliases=(Alias(text="R", style="letter"),),
        rationale="Single letter; strict neighbours exclude R&D.",
    ),
    Concept(
        concept_id="dotnet",
        label=".NET",
        kind="technology",
        aliases=(*_s(".NET"), *_w("dotnet")),
        rationale="Platform name; ASP.NET is a separate, narrower framework.",
    ),
    Concept(
        concept_id="aspnet",
        label="ASP.NET",
        kind="technology",
        aliases=_s("ASP.NET Core", "ASP.NET"),
        relations=_broader("dotnet"),
        rationale="Web framework on .NET; never equivalent to .NET.",
    ),
    Concept(
        concept_id="java",
        label="Java",
        kind="technology",
        aliases=_w("Java"),
        rationale="Word boundary keeps it distinct from JavaScript.",
    ),
    Concept(
        concept_id="javascript",
        label="JavaScript",
        kind="technology",
        aliases=(*_w("JavaScript"), *_a("JS")),
        rationale="JS is the common abbreviation; case-sensitive.",
    ),
    Concept(
        concept_id="typescript",
        label="TypeScript",
        kind="technology",
        aliases=_w("TypeScript"),
        rationale="TS is not aliased: it collides with other meanings.",
    ),
    Concept(
        concept_id="python",
        label="Python",
        kind="technology",
        aliases=_w("Python"),
        rationale="Version suffixes without a boundary (Python3) are not matched.",
    ),
    Concept(
        concept_id="nodejs",
        label="Node.js",
        kind="technology",
        aliases=(*_s("Node.js"), *_w("NodeJS")),
        rationale="Spelling variants.",
    ),
    Concept(
        concept_id="react",
        label="React",
        kind="technology",
        aliases=(*_a("React"), *_s("React.js"), *_w("ReactJS")),
        rationale="Case-sensitive to avoid the verb 'react'.",
    ),
    Concept(
        concept_id="postgresql",
        label="PostgreSQL",
        kind="technology",
        aliases=_w("PostgreSQL", "Postgres"),
        rationale="Common short name.",
    ),
    Concept(
        concept_id="mongodb",
        label="MongoDB",
        kind="technology",
        aliases=_w("MongoDB"),
        rationale="Product name.",
    ),
    Concept(
        concept_id="redis",
        label="Redis",
        kind="technology",
        aliases=_w("Redis"),
        rationale="Product name.",
    ),
    Concept(
        concept_id="neo4j",
        label="Neo4j",
        kind="technology",
        aliases=_w("Neo4j"),
        rationale="Product name.",
    ),
    Concept(
        concept_id="sql",
        label="SQL",
        kind="technology",
        aliases=_w("SQL"),
        rationale="Word boundaries keep PostgreSQL/NoSQL distinct.",
    ),
    Concept(
        concept_id="kubernetes",
        label="Kubernetes",
        kind="technology",
        aliases=(*_w("Kubernetes"), *_a("k8s")),
        rationale="k8s is the standard numeronym.",
    ),
    Concept(
        concept_id="docker",
        label="Docker",
        kind="technology",
        aliases=_w("Docker"),
        rationale="Product name.",
    ),
    Concept(
        concept_id="git", label="Git", kind="technology", aliases=_w("Git"), rationale="Tool name."
    ),
    Concept(
        concept_id="linux",
        label="Linux",
        kind="technology",
        aliases=_w("Linux"),
        rationale="Operating system family.",
    ),
    Concept(
        concept_id="ci-cd",
        label="CI/CD",
        kind="technology",
        aliases=_s("CI/CD"),
        rationale="Practice name; specific platforms are separate concepts.",
    ),
    Concept(
        concept_id="aws",
        label="AWS",
        kind="technology",
        aliases=(*_a("AWS"), *_w("Amazon Web Services")),
        rationale="Cloud provider; its services are narrower, never aliases.",
    ),
    Concept(
        concept_id="aws-sagemaker",
        label="Amazon SageMaker",
        kind="technology",
        aliases=_w("Amazon SageMaker", "SageMaker"),
        relations=_broader("aws"),
        rationale="AWS service; AWS experience does not imply it.",
    ),
    Concept(
        concept_id="aws-ec2",
        label="Amazon EC2",
        kind="technology",
        aliases=_w("Amazon EC2", "EC2"),
        relations=_broader("aws"),
        rationale="AWS service.",
    ),
    Concept(
        concept_id="aws-codepipeline",
        label="AWS CodePipeline",
        kind="technology",
        aliases=_w("AWS CodePipeline", "CodePipeline"),
        relations=_broader("aws"),
        rationale="AWS CI/CD service.",
    ),
    Concept(
        concept_id="azure",
        label="Azure",
        kind="technology",
        aliases=_w("Microsoft Azure", "Azure"),
        rationale="Cloud platform; Azure DevOps is a separate product.",
    ),
    Concept(
        concept_id="azure-devops",
        label="Azure DevOps",
        kind="technology",
        aliases=_w("Azure DevOps"),
        relations=_related("azure"),
        rationale="Developer services; not evidence of Azure hosting.",
    ),
    Concept(
        concept_id="azure-pipelines",
        label="Azure Pipelines",
        kind="technology",
        aliases=_w("Azure Pipelines"),
        relations=_broader("azure-devops"),
        rationale="CI/CD service within Azure DevOps.",
    ),
    Concept(
        concept_id="gcp",
        label="Google Cloud Platform",
        kind="technology",
        aliases=(*_a("GCP"), *_w("Google Cloud Platform", "Google Cloud")),
        rationale="Cloud provider.",
    ),
    Concept(
        concept_id="artificial-intelligence",
        label="Artificial intelligence",
        kind="field",
        aliases=(
            *_w("artificial intelligence", "künstliche Intelligenz", "künstlicher Intelligenz"),
            *_a("AI", "KI"),
        ),
        rationale="EN/DE field names; AI and KI are case-sensitive.",
    ),
    Concept(
        concept_id="machine-learning",
        label="Machine learning",
        kind="field",
        aliases=(
            *_w(
                "machine learning",
                "maschinelles Lernen",
                "maschinellem Lernen",
                "maschinellen Lernen",
                "maschinellen Lernens",
            ),
            *_a("ML"),
        ),
        relations=_broader("artificial-intelligence"),
        rationale="EN/DE forms with explicit German inflections; ML case-sensitive.",
    ),
    Concept(
        concept_id="deep-learning",
        label="Deep learning",
        kind="field",
        aliases=(*_w("deep learning"), *_a("DL")),
        relations=_broader("machine-learning"),
        rationale="Narrower field; frameworks such as PyTorch are related only.",
    ),
    Concept(
        concept_id="nlp",
        label="Natural language processing",
        kind="field",
        aliases=(*_w("natural language processing"), *_a("NLP")),
        relations=_broader("artificial-intelligence"),
        rationale="Field name.",
    ),
    Concept(
        concept_id="llm",
        label="Large language models",
        kind="field",
        aliases=(*_w("large language models", "large language model"), *_a("LLMs", "LLM")),
        relations=_related("nlp"),
        rationale="Model family; plural and singular.",
    ),
    Concept(
        concept_id="pytorch",
        label="PyTorch",
        kind="technology",
        aliases=_w("PyTorch"),
        relations=_related("deep-learning"),
        rationale="Framework; deep learning does not imply PyTorch or vice versa.",
    ),
    Concept(
        concept_id="tensorflow",
        label="TensorFlow",
        kind="technology",
        aliases=_w("TensorFlow"),
        relations=_related("deep-learning"),
        rationale="Framework.",
    ),
    Concept(
        concept_id="apache-spark",
        label="Apache Spark",
        kind="technology",
        aliases=(*_w("Apache Spark"), Alias(text="Spark", status="ambiguous")),
        rationale="'Spark' alone is an ordinary word too: candidate only.",
    ),
    Concept(
        concept_id="power-bi",
        label="Power BI",
        kind="technology",
        aliases=_w("Power BI"),
        rationale="Product name.",
    ),
    Concept(
        concept_id="dax",
        label="DAX",
        kind="technology",
        aliases=_w("DAX"),
        rationale="Power BI formula language. DAX is also a German stock index name; "
        "the caller's context (for example a technology requirement) decides relevance.",
    ),
    Concept(
        concept_id="lang-english",
        label="English",
        kind="language",
        aliases=_w("English", "Englisch", "Englischkenntnisse"),
        rationale="EN/DE names; no proficiency is implied.",
    ),
    Concept(
        concept_id="lang-german",
        label="German",
        kind="language",
        aliases=_w("German", "Deutsch", "Deutschkenntnisse"),
        rationale="EN/DE names; no proficiency is implied.",
    ),
    Concept(
        concept_id="lang-french",
        label="French",
        kind="language",
        aliases=_w("French", "Französisch", "Französischkenntnisse"),
        rationale="EN/DE names.",
    ),
    Concept(
        concept_id="lang-spanish",
        label="Spanish",
        kind="language",
        aliases=_w("Spanish", "Spanisch", "Spanischkenntnisse"),
        rationale="EN/DE names.",
    ),
)
