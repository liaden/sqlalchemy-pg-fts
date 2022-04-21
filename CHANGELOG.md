# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)
for the public APIs. `rubysys`, even though shared publicly, is considered a private
API and may have breaking changes during a teeny version change.

## [Unreleased]

## 0.1.3

- Filter additional punctuation related characters from websearch queries.

## 0.1.2

- Relax python version constraint for 3.6.

## 0.1.1

- Cleanup
- Fix `websearch` tokenization on Python 3.6

## 0.1.0

- Add `TSVector` as a column type.
- Add `TSQuery` as a column type.
- Add `to_tsvector` function.
- Add `to_tsquery` function.
- Add `websearch` to render tsquery text.
